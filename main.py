"""Programa de análisis financiero con ratios y DCF (perpetuidad + proyección)."""


def calcular_wacc_automatico(tipo_empresa, deuda_neta, ebitda):
    """Estima el WACC con una base por tipo de empresa y ajuste por apalancamiento."""
    wacc_base_tipo = {
        "growth": 0.10,
        "madura": 0.08,
        "defensiva": 0.07,
        "cíclica": 0.09,
    }

    if tipo_empresa not in wacc_base_tipo:
        print("Tipo de empresa no reconocido para WACC, se asume 'madura'.")
        tipo_empresa = "madura"

    wacc = wacc_base_tipo[tipo_empresa]
    justificacion = [f"WACC base para {tipo_empresa}: {wacc * 100:.2f}%"]

    apalancamiento = None
    if ebitda != 0:
        apalancamiento = deuda_neta / ebitda
        if apalancamiento > 4:
            wacc += 0.02
            justificacion.append("WACC ajustado al alza (+2%) por apalancamiento muy elevado (Deuda neta/EBITDA > 4).")
        elif apalancamiento > 3:
            wacc += 0.01
            justificacion.append("WACC ajustado al alza (+1%) por apalancamiento elevado (Deuda neta/EBITDA > 3).")
    else:
        justificacion.append("No se puede calcular Deuda neta/EBITDA por EBITDA=0; no se aplica ajuste por apalancamiento.")

    return wacc, apalancamiento, justificacion, tipo_empresa


def construir_crecimientos_decrecientes(g_inicial_pct, g_terminal_pct):
    """Genera g1..g5 linealmente decrecientes desde g_inicial hasta g_terminal."""
    paso = (g_inicial_pct - g_terminal_pct) / 5
    crecimientos = []
    for t in range(1, 6):
        g_t = g_inicial_pct - t * paso
        crecimientos.append(g_t)
    return crecimientos


def recopilar_datos():
    """Solicita inputs una sola vez y los guarda en un diccionario compartido."""
    datos = {}
    datos["tipo_empresa"] = input("Tipo de empresa (growth/madura/defensiva/cíclica): ").strip().lower()
    datos["ingresos"] = float(input("Ingresos: "))
    datos["ebitda"] = float(input("EBITDA: "))
    datos["fcf"] = float(input("FCF actual: "))
    datos["deuda"] = float(input("Deuda total: "))
    datos["caja"] = float(input("Caja disponible: "))
    datos["precio_accion"] = float(input("Precio de la acción: "))
    datos["patrimonio_neto"] = float(input("Patrimonio neto: "))
    datos["activos_totales"] = float(input("Activos totales: "))
    datos["beneficio_neto"] = float(input("Beneficio neto: "))
    datos["numero_acciones"] = float(input("Número de acciones: "))

    # Inputs para DCF: crecimiento (sin pedir WACC manual)
    print("\nSupuestos de crecimiento para DCF perpetuo (escenarios):")
    datos["g_conservador_pct"] = float(input("g conservador (%): "))
    datos["g_base_pct"] = float(input("g base (%): "))
    datos["g_optimista_pct"] = float(input("g optimista (%): "))

    print("\nSupuestos para DCF por proyección (5 años + terminal):")
    datos["g_inicial_pct"] = float(input("Crecimiento inicial (%): "))
    datos["g_terminal_pct"] = float(input("Crecimiento terminal (%): "))

    return datos


def calcular_ratios(datos):
    """Calcula ratios financieros, interpreta y genera veredicto preliminar."""
    ingresos = datos["ingresos"]
    ebitda = datos["ebitda"]
    fcf = datos["fcf"]
    deuda_neta = datos["deuda"] - datos["caja"]
    precio_accion = datos["precio_accion"]
    patrimonio_neto = datos["patrimonio_neto"]
    activos_totales = datos["activos_totales"]
    beneficio_neto = datos["beneficio_neto"]
    numero_acciones = datos["numero_acciones"]

    capitalizacion = precio_accion * numero_acciones
    ev = capitalizacion + deuda_neta

    print("\nResultados de ratios:")
    per = psr = ev_ebitda = ev_fcf = roe = roa = margen_ebitda = None

    if beneficio_neto == 0:
        print("No se puede calcular PER: divisor 0")
    else:
        per = capitalizacion / beneficio_neto
        print(f"PER: {per:.2f}")

    if ingresos == 0:
        print("No se puede calcular PSR: divisor 0")
    else:
        psr = capitalizacion / ingresos
        print(f"PSR: {psr:.2f}")

    if ebitda == 0:
        print("No se puede calcular EV/EBITDA: divisor 0")
    else:
        ev_ebitda = ev / ebitda
        print(f"EV/EBITDA: {ev_ebitda:.2f}")

    if fcf == 0:
        print("No se puede calcular EV/FCF: divisor 0")
    else:
        ev_fcf = ev / fcf
        print(f"EV/FCF: {ev_fcf:.2f}")

    if patrimonio_neto == 0:
        print("No se puede calcular ROE: divisor 0")
    else:
        roe = beneficio_neto / patrimonio_neto
        print(f"ROE: {roe:.2f}")

    if activos_totales == 0:
        print("No se puede calcular ROA: divisor 0")
    else:
        roa = beneficio_neto / activos_totales
        print(f"ROA: {roa:.2f}")

    if ingresos == 0:
        print("No se puede calcular Margen EBITDA: divisor 0")
    else:
        margen_ebitda = ebitda / ingresos
        print(f"Margen EBITDA: {margen_ebitda:.2f}")

    criterios = {
        "growth": {"per_razonable": 35, "ev_ebitda_razonable": 20},
        "madura": {"per_razonable": 20, "ev_ebitda_razonable": 12},
        "defensiva": {"per_razonable": 18, "ev_ebitda_razonable": 10},
        "cíclica": {"per_razonable": 22, "ev_ebitda_razonable": 14},
    }
    tipo = datos["tipo_empresa"] if datos["tipo_empresa"] in criterios else "madura"
    if tipo != datos["tipo_empresa"]:
        print("Tipo de empresa no reconocido, se asume 'madura'.")
    datos["tipo_empresa"] = tipo

    per_raz = criterios[tipo]["per_razonable"]
    ev_ebitda_raz = criterios[tipo]["ev_ebitda_razonable"]

    rentabilidad = []
    valoracion = []
    solvencia = []
    calidad_cash_flow = []

    print("\nInterpretación:")
    print(f"Nota: los criterios de PER y EV/EBITDA cambian según el perfil '{tipo}'.")

    if per is not None:
        if per < 15:
            valoracion.append("PER bajo (<15), sugiere valoración contenida.")
        elif per <= per_raz:
            valoracion.append(f"PER razonable para el perfil (≤{per_raz}).")
        else:
            valoracion.append(f"PER exigente para el perfil (>{per_raz}).")

    if ev_ebitda is not None:
        if ev_ebitda < 8:
            valoracion.append("EV/EBITDA bajo (<8), valoración atractiva.")
        elif ev_ebitda <= ev_ebitda_raz:
            valoracion.append(f"EV/EBITDA razonable para el perfil (≤{ev_ebitda_raz}).")
        else:
            valoracion.append(f"EV/EBITDA elevado para el perfil (>{ev_ebitda_raz}).")

    if ev_fcf is not None:
        if ev_fcf < 15:
            calidad_cash_flow.append("EV/FCF atractivo (<15), buena generación de caja.")
        elif ev_fcf <= 30:
            calidad_cash_flow.append("EV/FCF exigente (15–30), evaluar sostenibilidad del FCF.")
        else:
            calidad_cash_flow.append("EV/FCF muy exigente (>30), riesgo de sobrevaloración.")

    if roe is not None:
        if roe < 0.10:
            rentabilidad.append("ROE bajo (<10%), rentabilidad limitada.")
        elif roe <= 0.15:
            rentabilidad.append("ROE correcto (10–15%), rentabilidad adecuada.")
        else:
            rentabilidad.append("ROE elevado (>15%), rentabilidad sólida.")

    if margen_ebitda is not None:
        if margen_ebitda < 0.15:
            rentabilidad.append("Margen EBITDA bajo (<15%), presión operativa.")
        elif margen_ebitda <= 0.25:
            rentabilidad.append("Margen EBITDA normal (15–25%), eficiencia razonable.")
        else:
            rentabilidad.append("Margen EBITDA alto (>25%), elevada eficiencia.")

    if fcf <= 0:
        calidad_cash_flow.append("Advertencia: FCF ≤ 0, generación de caja débil.")
    if per is not None and per > 30:
        valoracion.append("Advertencia: PER > 30, posible sobrevaloración.")
    if ev_ebitda is not None and ev_ebitda > 25:
        valoracion.append("Advertencia: EV/EBITDA > 25, valoración exigente.")

    apalancamiento = None
    if ebitda != 0:
        apalancamiento = deuda_neta / ebitda
        if apalancamiento > 3:
            solvencia.append("Advertencia: Deuda neta/EBITDA > 3, apalancamiento elevado.")

    print("\nInforme resumido:")
    resumen = []
    if calidad_cash_flow:
        resumen.append("cash flow: " + "; ".join(calidad_cash_flow))
    if solvencia:
        resumen.append("riesgo financiero: " + "; ".join(solvencia))
    if valoracion:
        resumen.append("exigencia de valoración: " + "; ".join(valoracion))
    if rentabilidad:
        resumen.append("rentabilidad: " + "; ".join(rentabilidad))
    if resumen:
        print("La empresa presenta " + ". ".join(resumen) + ", lo que implica un perfil integral.")
    else:
        print("No hay suficiente información para elaborar un informe.")

    valoracion_exigente = (
        (per is not None and per > per_raz) or (ev_ebitda is not None and ev_ebitda > ev_ebitda_raz)
    )
    rentabilidad_sana = roe is not None and roe >= 0.10
    apalancamiento_alto = apalancamiento is not None and apalancamiento > 3

    veredicto = "neutral"
    if not valoracion_exigente and rentabilidad_sana and not apalancamiento_alto:
        veredicto = "favorable"
    elif valoracion_exigente or apalancamiento_alto or fcf <= 0:
        veredicto = "cautela"

    print(f"\nVeredicto preliminar basado en ratios: {veredicto}.")

    datos["ratios"] = {
        "per": per,
        "psr": psr,
        "ev_ebitda": ev_ebitda,
        "ev_fcf": ev_fcf,
        "roe": roe,
        "roa": roa,
        "margen_ebitda": margen_ebitda,
        "deuda_neta_ebitda": apalancamiento,
    }
    return veredicto


def calcular_dcf_perpetuidad(datos, veredicto_preliminar):
    """Modelo de perpetuidad como herramienta de control/comparación rápida."""
    fcf_actual = datos["fcf"]
    deuda_neta = datos["deuda"] - datos["caja"]
    numero_acciones = datos["numero_acciones"]

    wacc = datos["wacc"]
    wacc_conservador = wacc + 0.01
    wacc_base = wacc
    wacc_optimista = max(wacc - 0.01, 0.0001)

    print("\nResultados del DCF perpetuo:")
    if fcf_actual <= 0:
        print("Advertencia: FCF ≤ 0, el DCF puede no ser fiable.")

    def calcular_escenario(nombre, g_pct, wacc_esc):
        g = g_pct / 100
        if wacc_esc <= 0:
            print(f"{nombre}: No se puede calcular Valor empresa: WACC <= 0.")
            return None
        if g >= wacc_esc:
            print(f"{nombre}: Error crítico, g ≥ WACC. Revisa los supuestos.")
            return None

        valor_empresa = fcf_actual * (1 + g) / (wacc_esc - g)
        valor_equity = valor_empresa - deuda_neta
        if numero_acciones == 0:
            print(f"{nombre}: No se puede calcular Precio teórico por acción: divisor 0.")
            return None

        precio_teorico = valor_equity / numero_acciones
        print(f"{nombre} - WACC: {wacc_esc * 100:.2f}%")
        print(f"{nombre} - Valor empresa: {valor_empresa:.2f}")
        print(f"{nombre} - Valor equity: {valor_equity:.2f}")
        print(f"{nombre} - Precio teórico por acción: {precio_teorico:.2f}")
        return precio_teorico

    calcular_escenario("Conservador", datos["g_conservador_pct"], wacc_conservador)
    precio_base = calcular_escenario("Base", datos["g_base_pct"], wacc_base)
    calcular_escenario("Optimista", datos["g_optimista_pct"], wacc_optimista)

    precio_mercado = datos["precio_accion"]
    if precio_base is not None and precio_mercado > 0:
        diferencia_pct = (precio_mercado - precio_base) / precio_base
        print("\nClasificación según precio de mercado (DCF perpetuo base):")
        if diferencia_pct < -0.20:
            print("Infravalorada: precio >20% por debajo del DCF base.")
        elif diferencia_pct <= 0.20:
            print("Precio razonable: mercado dentro de ±20% del DCF base.")
        else:
            print("Sobrevalorada: precio >20% por encima del DCF base.")

        print("\nValidación del veredicto preliminar:")
        if diferencia_pct < -0.20 and veredicto_preliminar == "cautela":
            print("Alerta: múltiplos exigentes pero DCF base superior al precio actual.")
        elif diferencia_pct > 0.20 and veredicto_preliminar == "favorable":
            print("Alerta: ratios favorables, pero DCF base queda por debajo del precio actual.")
        else:
            print("El DCF base es coherente con el veredicto preliminar.")

    return precio_base


def calcular_dcf_proyeccion(datos):
    """DCF con proyección explícita de 5 años + valor terminal."""
    fcf_actual = datos["fcf"]
    wacc = datos["wacc"]
    g_terminal_pct = datos["g_terminal_pct"]
    g_terminal = g_terminal_pct / 100

    if fcf_actual <= 0:
        print("Advertencia: FCF0 ≤ 0, la proyección puede no ser fiable.")

    crecimientos = construir_crecimientos_decrecientes(datos["g_inicial_pct"], g_terminal_pct)
    if any(g > 40 for g in crecimientos):
        print("Advertencia: algún crecimiento g_t es extremadamente alto (>40%).")
    elif any(g > 30 for g in crecimientos):
        print("Advertencia: algún crecimiento g_t es muy alto (>30%).")

    if g_terminal >= wacc:
        print("Error crítico: g terminal ≥ WACC. Revisa los supuestos.")
        return None
    if wacc <= 0:
        print("Error crítico: WACC <= 0. Revisa los supuestos.")
        return None

    print("\nTabla de crecimientos automáticos (lineal decreciente):")
    for i, g in enumerate(crecimientos, start=1):
        print(f"g{i}: {g:.2f}%")

    print("\nProyección de FCF y valores presentes:")
    fcf_t = fcf_actual
    vp_fcfs = []
    fcfs = []
    for i, g_pct in enumerate(crecimientos, start=1):
        fcf_t = fcf_t * (1 + g_pct / 100)
        vp = fcf_t / ((1 + wacc) ** i)
        fcfs.append(fcf_t)
        vp_fcfs.append(vp)
        print(f"Año {i} - FCF: {fcf_t:.2f} | VP: {vp:.2f}")

    valor_terminal = (fcfs[-1] * (1 + g_terminal)) / (wacc - g_terminal)
    vp_valor_terminal = valor_terminal / ((1 + wacc) ** 5)
    valor_empresa = sum(vp_fcfs) + vp_valor_terminal

    deuda_neta = datos["deuda"] - datos["caja"]
    valor_equity = valor_empresa - deuda_neta
    if datos["numero_acciones"] == 0:
        print("No se puede calcular Precio teórico por acción: divisor 0.")
        return None

    precio_teorico = valor_equity / datos["numero_acciones"]
    peso_terminal = vp_valor_terminal / valor_empresa if valor_empresa != 0 else 0
    if peso_terminal > 0.70:
        print("Advertencia: el valor terminal representa >70% del EV total.")

    print(f"Valor terminal: {valor_terminal:.2f}")
    print(f"VP del valor terminal: {vp_valor_terminal:.2f}")
    print(f"Peso del valor terminal en EV: {peso_terminal:.2%}")
    print(f"Valor empresa total (EV): {valor_empresa:.2f}")
    print(f"Valor del equity: {valor_equity:.2f}")
    print(f"Precio teórico por acción: {precio_teorico:.2f}")

    precio_mercado = datos["precio_accion"]
    if precio_mercado > 0:
        diferencia_pct = (precio_mercado - precio_teorico) / precio_teorico
        print("\nClasificación según precio de mercado (DCF 5 años):")
        if diferencia_pct < -0.20:
            print("Infravalorada: precio >20% por debajo del DCF a 5 años.")
        elif diferencia_pct <= 0.20:
            print("Precio razonable: mercado dentro de ±20% del DCF a 5 años.")
        else:
            print("Sobrevalorada: precio >20% por encima del DCF a 5 años.")

    return precio_teorico


def calcular_investment_score(datos, precio_dcf_base):
    """Calcula score 0-100 con desglose por bloques."""
    r = datos["ratios"]

    # Valoración (40)
    score_val = 0
    if r["per"] is not None:
        score_val += 14 if r["per"] < 15 else 10 if r["per"] <= 25 else 4
    if r["ev_ebitda"] is not None:
        score_val += 14 if r["ev_ebitda"] < 8 else 10 if r["ev_ebitda"] <= 15 else 4
    if r["ev_fcf"] is not None:
        score_val += 12 if r["ev_fcf"] < 15 else 8 if r["ev_fcf"] <= 30 else 2

    # Rentabilidad (25)
    score_ren = 0
    if r["roe"] is not None:
        score_ren += 13 if r["roe"] > 0.15 else 9 if r["roe"] >= 0.10 else 4
    if r["margen_ebitda"] is not None:
        score_ren += 12 if r["margen_ebitda"] > 0.25 else 8 if r["margen_ebitda"] >= 0.15 else 3

    # Riesgo financiero (20)
    score_riesgo = 0
    de = r["deuda_neta_ebitda"]
    if de is not None:
        score_riesgo += 12 if de <= 2 else 8 if de <= 3 else 3
    score_riesgo += 8 if datos["fcf"] > 0 else 2

    # DCF vs mercado (15)
    score_dcf = 0
    if precio_dcf_base is not None and precio_dcf_base != 0:
        diff = (datos["precio_accion"] - precio_dcf_base) / precio_dcf_base
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

    print("\nInvestment Score (0-100):")
    print(f"Valoración (40): {score_val:.0f}")
    print(f"Rentabilidad (25): {score_ren:.0f}")
    print(f"Riesgo financiero (20): {score_riesgo:.0f}")
    print(f"DCF vs mercado (15): {score_dcf:.0f}")
    print(f"Score total: {total:.0f}")
    print(f"Clasificación final: {clasificacion}")


def main():
    """Ejecución principal del análisis."""
    datos = recopilar_datos()
    deuda_neta = datos["deuda"] - datos["caja"]
    wacc, apalancamiento, justificacion_wacc, tipo_validado = calcular_wacc_automatico(
        datos["tipo_empresa"], deuda_neta, datos["ebitda"]
    )
    datos["tipo_empresa"] = tipo_validado
    datos["wacc"] = wacc

    print("\nWACC automático estimado:")
    print(f"WACC final: {wacc * 100:.2f}%")
    for j in justificacion_wacc:
        print(f"- {j}")
    if apalancamiento is not None:
        print(f"- Deuda neta/EBITDA calculada: {apalancamiento:.2f}")

    veredicto = calcular_ratios(datos)
    precio_perpetuo = calcular_dcf_perpetuidad(datos, veredicto)

    print("\nDCF por proyección explícita (5 años + valor terminal):")
    print("Modelo recomendado para empresas growth o en transición.")
    precio_proyeccion = calcular_dcf_proyeccion(datos)

    if precio_perpetuo is not None and precio_proyeccion is not None:
        print("\nComparación entre modelos DCF:")
        if precio_proyeccion < precio_perpetuo:
            print(
                "El DCF por proyección arroja un valor inferior al perpetuo debido a la "
                "desaceleración del crecimiento y/o mayor riesgo en fase de transición."
            )
        elif precio_proyeccion > precio_perpetuo:
            print(
                "El DCF por proyección arroja un valor superior al perpetuo por una fase "
                "de crecimiento inicial más intensa antes de madurez."
            )
        else:
            print("Ambos DCF son coherentes, con supuestos de crecimiento similares.")

    calcular_investment_score(datos, precio_perpetuo)


if __name__ == "__main__":
    main()
