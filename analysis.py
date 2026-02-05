"""Lógica financiera para la mini app de análisis de inversión.

Este módulo separa cálculos y reglas de negocio de la interfaz Streamlit.
"""


def calcular_wacc_automatico(tipo_empresa, deuda_neta, ebitda):
    """Estima WACC por tipo de empresa y ajuste de apalancamiento."""
    wacc_base_tipo = {
        "growth": 0.10,
        "madura": 0.08,
        "defensiva": 0.07,
        "cíclica": 0.09,
    }

    if tipo_empresa not in wacc_base_tipo:
        tipo_empresa = "madura"

    wacc = wacc_base_tipo[tipo_empresa]
    justificacion = [f"WACC base para {tipo_empresa}: {wacc * 100:.2f}%"]

    deuda_neta_ebitda = None
    if ebitda != 0:
        deuda_neta_ebitda = deuda_neta / ebitda
        if deuda_neta_ebitda > 4:
            wacc += 0.02
            justificacion.append("WACC ajustado al alza por apalancamiento muy elevado (>4x).")
        elif deuda_neta_ebitda > 3:
            wacc += 0.01
            justificacion.append("WACC ajustado al alza por apalancamiento elevado (>3x).")
    else:
        justificacion.append("Sin ajuste de apalancamiento: EBITDA es 0.")

    return {
        "tipo_empresa": tipo_empresa,
        "wacc": wacc,
        "deuda_neta_ebitda": deuda_neta_ebitda,
        "justificacion": justificacion,
    }


def construir_crecimientos_decrecientes(g_inicial_pct, g_terminal_pct):
    """Genera g1..g5 lineal decreciente usando la fórmula solicitada."""
    paso = (g_inicial_pct - g_terminal_pct) / 5
    return [g_inicial_pct - t * paso for t in range(1, 6)]


def calcular_ratios(datos):
    """Calcula ratios clave e interpretación cualitativa."""
    capitalizacion = datos["precio_accion"] * datos["numero_acciones"]
    deuda_neta = datos["deuda"] - datos["caja"]
    ev = capitalizacion + deuda_neta

    ratios = {
        "PER": None,
        "PSR": None,
        "EV/EBITDA": None,
        "EV/FCF": None,
        "ROE": None,
        "ROA": None,
        "Margen EBITDA": None,
        "Capitalización": capitalizacion,
        "EV": ev,
    }
    advertencias = []
    rentabilidad = []
    valoracion = []
    solvencia = []
    calidad_cash_flow = []

    if datos["beneficio_neto"] != 0:
        ratios["PER"] = capitalizacion / datos["beneficio_neto"]
    if datos["ingresos"] != 0:
        ratios["PSR"] = capitalizacion / datos["ingresos"]
        ratios["Margen EBITDA"] = datos["ebitda"] / datos["ingresos"]
    if datos["ebitda"] != 0:
        ratios["EV/EBITDA"] = ev / datos["ebitda"]
    if datos["fcf"] != 0:
        ratios["EV/FCF"] = ev / datos["fcf"]
    if datos["patrimonio_neto"] != 0:
        ratios["ROE"] = datos["beneficio_neto"] / datos["patrimonio_neto"]
    if datos["activos_totales"] != 0:
        ratios["ROA"] = datos["beneficio_neto"] / datos["activos_totales"]

    # Interpretación por rangos estándar.
    per = ratios["PER"]
    ev_ebitda = ratios["EV/EBITDA"]
    ev_fcf = ratios["EV/FCF"]
    roe = ratios["ROE"]
    margen = ratios["Margen EBITDA"]

    if per is not None:
        if per < 15:
            valoracion.append("PER bajo (<15).")
        elif per <= 25:
            valoracion.append("PER razonable (15–25).")
        else:
            valoracion.append("PER exigente (>25).")
        if per > 30:
            advertencias.append("PER > 30: posible sobrevaloración.")

    if ev_ebitda is not None:
        if ev_ebitda < 8:
            valoracion.append("EV/EBITDA bajo (<8).")
        elif ev_ebitda <= 15:
            valoracion.append("EV/EBITDA razonable (8–15).")
        else:
            valoracion.append("EV/EBITDA elevado (>15).")
        if ev_ebitda > 25:
            advertencias.append("EV/EBITDA > 25: valoración exigente.")

    if ev_fcf is not None:
        if ev_fcf < 15:
            calidad_cash_flow.append("EV/FCF atractivo (<15).")
        elif ev_fcf <= 30:
            calidad_cash_flow.append("EV/FCF exigente (15–30).")
        else:
            calidad_cash_flow.append("EV/FCF muy exigente (>30).")

    if roe is not None:
        if roe < 0.10:
            rentabilidad.append("ROE bajo (<10%).")
        elif roe <= 0.15:
            rentabilidad.append("ROE correcto (10–15%).")
        else:
            rentabilidad.append("ROE elevado (>15%).")

    if margen is not None:
        if margen < 0.15:
            rentabilidad.append("Margen EBITDA bajo (<15%).")
        elif margen <= 0.25:
            rentabilidad.append("Margen EBITDA normal (15–25%).")
        else:
            rentabilidad.append("Margen EBITDA alto (>25%).")

    if datos["fcf"] <= 0:
        advertencias.append("FCF ≤ 0: generación de caja débil.")
        calidad_cash_flow.append("FCF débil o negativo.")

    deuda_neta_ebitda = None
    if datos["ebitda"] != 0:
        deuda_neta_ebitda = deuda_neta / datos["ebitda"]
        if deuda_neta_ebitda > 3:
            advertencias.append("Deuda neta/EBITDA > 3: apalancamiento elevado.")
            solvencia.append("Apalancamiento alto.")

    valoracion_exigente = (per is not None and per > 25) or (ev_ebitda is not None and ev_ebitda > 15)
    rentabilidad_sana = roe is not None and roe >= 0.10
    apalancamiento_alto = deuda_neta_ebitda is not None and deuda_neta_ebitda > 3

    veredicto = "neutral"
    if not valoracion_exigente and rentabilidad_sana and not apalancamiento_alto:
        veredicto = "favorable"
    elif valoracion_exigente or apalancamiento_alto or datos["fcf"] <= 0:
        veredicto = "cautela"

    return {
        "ratios": ratios,
        "deuda_neta_ebitda": deuda_neta_ebitda,
        "rentabilidad": rentabilidad,
        "valoracion": valoracion,
        "solvencia": solvencia,
        "calidad_cash_flow": calidad_cash_flow,
        "advertencias": advertencias,
        "veredicto_preliminar": veredicto,
    }


def calcular_dcf_perpetuo(datos, wacc):
    """DCF perpetuo en 3 escenarios (conservador/base/optimista)."""
    fcf = datos["fcf"]
    deuda_neta = datos["deuda"] - datos["caja"]
    n_acc = datos["numero_acciones"]

    escenarios = {
        "Conservador": (datos["g_conservador_pct"] / 100, wacc + 0.01),
        "Base": (datos["g_base_pct"] / 100, wacc),
        "Optimista": (datos["g_optimista_pct"] / 100, max(wacc - 0.01, 0.0001)),
    }

    resultados = {}
    advertencias = []
    for nombre, (g, wacc_esc) in escenarios.items():
        if g >= wacc_esc:
            resultados[nombre] = {"error": "Error crítico: g ≥ WACC."}
            continue
        if wacc_esc <= 0:
            resultados[nombre] = {"error": "Error crítico: WACC <= 0."}
            continue
        if n_acc == 0:
            resultados[nombre] = {"error": "No se puede calcular precio: Nº de acciones = 0."}
            continue

        valor_empresa = fcf * (1 + g) / (wacc_esc - g)
        valor_equity = valor_empresa - deuda_neta
        precio = valor_equity / n_acc
        resultados[nombre] = {
            "g": g,
            "wacc": wacc_esc,
            "valor_empresa": valor_empresa,
            "valor_equity": valor_equity,
            "precio": precio,
        }

    precio_base = resultados.get("Base", {}).get("precio")
    clasificacion = None
    if precio_base is not None and precio_base != 0:
        diff = (datos["precio_accion"] - precio_base) / precio_base
        if diff < -0.20:
            clasificacion = "Infravalorada"
        elif diff <= 0.20:
            clasificacion = "Precio razonable"
        else:
            clasificacion = "Sobrevalorada"

    if datos["fcf"] <= 0:
        advertencias.append("FCF ≤ 0: el DCF perpetuo puede no ser fiable.")

    return {
        "escenarios": resultados,
        "precio_base": precio_base,
        "clasificacion_mercado": clasificacion,
        "advertencias": advertencias,
    }


def calcular_dcf_proyeccion(datos, wacc):
    """DCF de 5 años + valor terminal con crecimientos automáticos."""
    fcf0 = datos["fcf"]
    g_terminal = datos["g_terminal_pct"] / 100
    deuda_neta = datos["deuda"] - datos["caja"]
    n_acc = datos["numero_acciones"]

    advertencias = []
    if fcf0 <= 0:
        advertencias.append("FCF0 ≤ 0: la proyección puede no ser fiable.")

    crecimientos = construir_crecimientos_decrecientes(datos["g_inicial_pct"], datos["g_terminal_pct"])
    if any(g > 40 for g in crecimientos):
        advertencias.append("Algún crecimiento g_t es extremadamente alto (>40%).")
    elif any(g > 30 for g in crecimientos):
        advertencias.append("Algún crecimiento g_t es muy alto (>30%).")

    if g_terminal >= wacc:
        return {"error": "Error crítico: g_terminal ≥ WACC.", "advertencias": advertencias}
    if wacc <= 0:
        return {"error": "Error crítico: WACC <= 0.", "advertencias": advertencias}
    if n_acc == 0:
        return {"error": "No se puede calcular precio: Nº de acciones = 0.", "advertencias": advertencias}

    fcfs = []
    vps = []
    fcf_t = fcf0
    for t, g_pct in enumerate(crecimientos, start=1):
        fcf_t = fcf_t * (1 + g_pct / 100)
        vp = fcf_t / ((1 + wacc) ** t)
        fcfs.append(fcf_t)
        vps.append(vp)

    valor_terminal = (fcfs[-1] * (1 + g_terminal)) / (wacc - g_terminal)
    vp_terminal = valor_terminal / ((1 + wacc) ** 5)
    ev = sum(vps) + vp_terminal
    equity = ev - deuda_neta
    precio = equity / n_acc

    peso_terminal = vp_terminal / ev if ev != 0 else 0
    if peso_terminal > 0.70:
        advertencias.append("El valor terminal representa >70% del EV total.")

    clasificacion = None
    if precio != 0:
        diff = (datos["precio_accion"] - precio) / precio
        if diff < -0.20:
            clasificacion = "Infravalorada"
        elif diff <= 0.20:
            clasificacion = "Precio razonable"
        else:
            clasificacion = "Sobrevalorada"

    return {
        "crecimientos_pct": crecimientos,
        "fcf_proyectados": fcfs,
        "vp_fcfs": vps,
        "valor_terminal": valor_terminal,
        "vp_terminal": vp_terminal,
        "peso_terminal": peso_terminal,
        "ev": ev,
        "equity": equity,
        "precio": precio,
        "clasificacion_mercado": clasificacion,
        "advertencias": advertencias,
    }


def calcular_investment_score(ratios, fcf, precio_mercado, precio_dcf_base):
    """Score cuantitativo 0-100 con desglose por bloques."""
    score_val = 0
    per = ratios["PER"]
    ev_ebitda = ratios["EV/EBITDA"]
    ev_fcf = ratios["EV/FCF"]

    if per is not None:
        score_val += 14 if per < 15 else 10 if per <= 25 else 4
    if ev_ebitda is not None:
        score_val += 14 if ev_ebitda < 8 else 10 if ev_ebitda <= 15 else 4
    if ev_fcf is not None:
        score_val += 12 if ev_fcf < 15 else 8 if ev_fcf <= 30 else 2

    score_ren = 0
    roe = ratios["ROE"]
    margen = ratios["Margen EBITDA"]
    if roe is not None:
        score_ren += 13 if roe > 0.15 else 9 if roe >= 0.10 else 4
    if margen is not None:
        score_ren += 12 if margen > 0.25 else 8 if margen >= 0.15 else 3

    score_riesgo = 0
    dneb = ratios.get("Deuda neta/EBITDA")
    if dneb is not None:
        score_riesgo += 12 if dneb <= 2 else 8 if dneb <= 3 else 3
    score_riesgo += 8 if fcf > 0 else 2

    score_dcf = 0
    if precio_dcf_base is not None and precio_dcf_base != 0:
        diff = (precio_mercado - precio_dcf_base) / precio_dcf_base
        if diff < -0.20:
            score_dcf = 15
        elif diff <= 0.20:
            score_dcf = 10
        else:
            score_dcf = 4

    total = max(0, min(100, score_val + score_ren + score_riesgo + score_dcf))
    if total >= 75:
        clasificacion = "Compra"
    elif total >= 60:
        clasificacion = "Mantener"
    elif total >= 45:
        clasificacion = "Neutral"
    else:
        clasificacion = "Evitar"

    return {
        "valoracion": score_val,
        "rentabilidad": score_ren,
        "riesgo": score_riesgo,
        "dcf_vs_mercado": score_dcf,
        "total": total,
        "clasificacion": clasificacion,
    }


def ejecutar_analisis(datos):
    """Orquesta el análisis completo para la interfaz web."""
    deuda_neta = datos["deuda"] - datos["caja"]
    wacc_info = calcular_wacc_automatico(datos["tipo_empresa"], deuda_neta, datos["ebitda"])
    datos["tipo_empresa"] = wacc_info["tipo_empresa"]

    ratios_info = calcular_ratios(datos)
    ratios_info["ratios"]["Deuda neta/EBITDA"] = wacc_info["deuda_neta_ebitda"]

    dcf_perpetuo = calcular_dcf_perpetuo(datos, wacc_info["wacc"])
    dcf_proyeccion = calcular_dcf_proyeccion(datos, wacc_info["wacc"])

    score = calcular_investment_score(
        ratios_info["ratios"],
        datos["fcf"],
        datos["precio_accion"],
        dcf_perpetuo["precio_base"],
    )

    comparacion = None
    precio_perpetuo = dcf_perpetuo["precio_base"]
    precio_proyeccion = dcf_proyeccion.get("precio") if isinstance(dcf_proyeccion, dict) else None
    if precio_perpetuo is not None and precio_proyeccion is not None:
        if precio_proyeccion < precio_perpetuo:
            comparacion = (
                "El DCF por proyección arroja un valor inferior al perpetuo debido a la "
                "desaceleración del crecimiento prevista."
            )
        elif precio_proyeccion > precio_perpetuo:
            comparacion = (
                "El DCF por proyección arroja un valor superior al perpetuo por una "
                "fase inicial de crecimiento más intensa."
            )
        else:
            comparacion = "Ambos DCF son coherentes con supuestos de crecimiento similares."

    return {
        "wacc_info": wacc_info,
        "ratios_info": ratios_info,
        "dcf_perpetuo": dcf_perpetuo,
        "dcf_proyeccion": dcf_proyeccion,
        "score": score,
        "comparacion_dcf": comparacion,
    }
