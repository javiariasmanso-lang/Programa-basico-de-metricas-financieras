"""Programa básico de métricas financieras."""


def calcular_ratios():
    """Solicita datos financieros y calcula ratios básicos."""
    tipo_empresa = input("Tipo de empresa (growth/madura/defensiva/cíclica): ").strip().lower()
    ingresos = float(input("Ingresos: "))
    ebitda = float(input("EBITDA: "))
    fcf = float(input("FCF: "))
    deuda = float(input("Deuda: "))
    caja = float(input("Caja disponible: "))
    precio_accion = float(input("Precio de la acción: "))
    patrimonio_neto = float(input("Patrimonio neto: "))
    activos_totales = float(input("Activos totales: "))
    beneficio_neto = float(input("Beneficio neto: "))
    numero_acciones = float(input("Número de acciones: "))

    # Cálculo de capitalización, deuda neta y valor de empresa (EV)
    capitalizacion = precio_accion * numero_acciones
    deuda_neta = deuda - caja
    ev = capitalizacion + deuda_neta

    print("\nResultados de ratios:")
    per = None
    ev_ebitda = None
    ev_fcf = None
    roe = None
    margen_ebitda = None

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
    if tipo_empresa not in criterios:
        print("Tipo de empresa no reconocido, se asume 'madura'.")
        tipo_empresa = "madura"

    per_razonable = criterios[tipo_empresa]["per_razonable"]
    ev_ebitda_razonable = criterios[tipo_empresa]["ev_ebitda_razonable"]

    rentabilidad = []
    valoracion = []
    solvencia = []
    calidad_cash_flow = []

    print("\nInterpretación:")
    print(
        f"Nota: los criterios de PER y EV/EBITDA cambian según el perfil '{tipo_empresa}'."
    )
    if per is not None:
        if per < 15:
            valoracion.append("PER bajo, sugiere valoración contenida.")
        elif per <= per_razonable:
            valoracion.append(
                f"PER razonable para el perfil (≤{per_razonable})."
            )
        else:
            valoracion.append(
                f"PER exigente para el perfil (>{per_razonable})."
            )
    if ev_ebitda is not None:
        if ev_ebitda < 8:
            valoracion.append("EV/EBITDA bajo, valoración atractiva.")
        elif ev_ebitda <= ev_ebitda_razonable:
            valoracion.append(
                f"EV/EBITDA razonable para el perfil (≤{ev_ebitda_razonable})."
            )
        else:
            valoracion.append(
                f"EV/EBITDA elevado para el perfil (>{ev_ebitda_razonable})."
            )
    if ev_fcf is not None:
        if ev_fcf < 15:
            calidad_cash_flow.append("EV/FCF atractivo, buena generación de caja.")
        elif ev_fcf <= 30:
            calidad_cash_flow.append("EV/FCF exigente, evaluar sostenibilidad del FCF.")
        else:
            calidad_cash_flow.append("EV/FCF muy exigente, riesgo de sobrevaloración.")
    if roe is not None:
        if roe < 0.10:
            rentabilidad.append("ROE bajo, rentabilidad sobre capital limitada.")
        elif roe <= 0.15:
            rentabilidad.append("ROE correcto, rentabilidad adecuada.")
        else:
            rentabilidad.append("ROE elevado, rentabilidad sólida.")
    if margen_ebitda is not None:
        if margen_ebitda < 0.15:
            rentabilidad.append("Margen EBITDA bajo, presión en la rentabilidad operativa.")
        elif margen_ebitda <= 0.25:
            rentabilidad.append("Margen EBITDA normal, eficiencia operativa razonable.")
        else:
            rentabilidad.append("Margen EBITDA alto, elevada eficiencia operativa.")
    if fcf <= 0:
        calidad_cash_flow.append("Advertencia: FCF ≤ 0, generación de caja débil.")
    if per is not None and per > 30:
        valoracion.append("Advertencia: PER > 30, posible sobrevaloración.")
    if ebitda != 0:
        apalancamiento = deuda_neta / ebitda
        if apalancamiento > 3:
            solvencia.append("Apalancamiento elevado (Deuda neta/EBITDA > 3).")
    if ev_ebitda is not None and ev_ebitda > 25:
        valoracion.append("Advertencia: EV/EBITDA > 25, valoración exigente.")

    # Las conclusiones anteriores ya incorporan los umbrales por perfil.

    print("\nInforme resumido:")
    resumen_partes = []
    if calidad_cash_flow:
        resumen_partes.append("cash flow: " + "; ".join(calidad_cash_flow))
    if solvencia:
        resumen_partes.append("riesgo financiero: " + "; ".join(solvencia))
    if valoracion:
        resumen_partes.append("exigencia de valoración: " + "; ".join(valoracion))
    if rentabilidad:
        resumen_partes.append("rentabilidad: " + "; ".join(rentabilidad))
    if resumen_partes:
        print("La empresa presenta " + ". ".join(resumen_partes) + ", lo que implica un perfil integral.")
    else:
        print("No hay suficiente información para elaborar un informe.")

    veredicto = "neutral"
    valoracion_exigente = (
        (per is not None and per > per_razonable)
        or (ev_ebitda is not None and ev_ebitda > ev_ebitda_razonable)
    )
    rentabilidad_sana = roe is not None and roe >= 0.10
    apalancamiento_alto = ebitda != 0 and (deuda_neta / ebitda) > 3
    if not valoracion_exigente and rentabilidad_sana and not apalancamiento_alto:
        veredicto = "favorable"
    elif valoracion_exigente or apalancamiento_alto or fcf <= 0:
        veredicto = "cautela"

    print(f"\nVeredicto preliminar basado en ratios: {veredicto}.")

    return {"precio": precio_accion, "veredicto": veredicto}


def calcular_dcf_perpetuidad(precio_mercado, veredicto_preliminar):
    """Calcula el valor teórico por acción con un modelo DCF perpetuo."""
    fcf_actual = float(input("FCF actual: "))
    deuda = float(input("Deuda: "))
    caja = float(input("Caja disponible: "))
    numero_acciones = float(input("Nº de acciones: "))

    print("\nEscenarios de DCF (introducir porcentajes):")
    g_conservador = float(input("g conservador (%): "))
    wacc_conservador = float(input("WACC conservador (%): "))
    g_base = float(input("g base (%): "))
    wacc_base = float(input("WACC base (%): "))
    g_optimista = float(input("g optimista (%): "))
    wacc_optimista = float(input("WACC optimista (%): "))

    print("\nResultados del DCF:")
    deuda_neta = deuda - caja

    if fcf_actual <= 0:
        print("Advertencia: FCF ≤ 0, el DCF puede no ser fiable.")

    def calcular_escenario(nombre, g_pct, wacc_pct):
        g = g_pct / 100
        wacc = wacc_pct / 100
        if wacc <= 0:
            print(f"{nombre}: No se puede calcular Valor empresa: WACC <= 0.")
            return None
        if g >= wacc:
            print(f"{nombre}: Error crítico, g ≥ WACC. Revisa los supuestos.")
            return None
        valor_empresa = fcf_actual * (1 + g) / (wacc - g)
        valor_equity = valor_empresa - deuda_neta
        if numero_acciones == 0:
            print(f"{nombre}: No se puede calcular Precio teórico por acción: divisor 0.")
            return None
        precio_teorico = valor_equity / numero_acciones
        print(f"{nombre} - Valor empresa: {valor_empresa:.2f}")
        print(f"{nombre} - Valor equity: {valor_equity:.2f}")
        print(f"{nombre} - Precio teórico por acción: {precio_teorico:.2f}")
        return precio_teorico

    calcular_escenario("Conservador", g_conservador, wacc_conservador)
    precio_base = calcular_escenario("Base", g_base, wacc_base)
    calcular_escenario("Optimista", g_optimista, wacc_optimista)

    if precio_base is not None and precio_mercado > 0:
        diferencia_pct = (precio_mercado - precio_base) / precio_base
        print("\nClasificación según precio de mercado (DCF perpetuo base):")
        if diferencia_pct < -0.20:
            print(
                "Infravalorada: el precio de mercado está >20% por debajo del DCF base, "
                "lo que sugiere margen de seguridad si el crecimiento y el cash flow se sostienen."
            )
        elif diferencia_pct <= 0.20:
            print(
                "Precio razonable: el mercado está dentro de ±20% del DCF base, "
                "lo que indica valoración equilibrada frente a riesgo y crecimiento."
            )
        else:
            print(
                "Sobrevalorada: el precio de mercado está >20% por encima del DCF base, "
                "lo que exige crecimiento elevado y un cash flow robusto."
            )
        print("\nValidación del veredicto preliminar:")
        if diferencia_pct < -0.20 and veredicto_preliminar == "cautela":
            print(
                "Alerta: aunque los ratios sugieren cautela, el DCF base indica valor superior "
                "al precio actual, lo que podría justificar parte del riesgo asumido."
            )
        elif diferencia_pct > 0.20 and veredicto_preliminar == "favorable":
            print(
                "Alerta: aunque los ratios sugieren un perfil favorable, el DCF base queda por "
                "debajo del precio actual, lo que contradice el veredicto preliminar."
            )
        else:
            print("El DCF base es coherente con el veredicto preliminar.")

    return precio_base

def calcular_dcf_proyeccion(precio_mercado):
    """Calcula un DCF con proyección explícita a 5 años y valor terminal."""
    fcf_actual = float(input("FCF actual (FCF0): "))
    crecimientos = []
    for i in range(1, 6):
        crecimientos.append(float(input(f"g{i} (%): ")))
    wacc_pct = float(input("WACC (%): "))
    g_terminal_pct = float(input("g terminal (%): "))
    deuda = float(input("Deuda total: "))
    caja = float(input("Caja disponible: "))
    numero_acciones = float(input("Nº de acciones: "))

    if fcf_actual <= 0:
        print("Advertencia: FCF0 ≤ 0, la proyección puede no ser fiable.")
    if any(g > 30 for g in crecimientos):
        print("Advertencia: algún crecimiento gᵗ es extremadamente alto (>30%).")

    wacc = wacc_pct / 100
    g_terminal = g_terminal_pct / 100

    if g_terminal >= wacc:
        print("Error crítico: g terminal ≥ WACC. Revisa los supuestos.")
        return None
    if wacc <= 0:
        print("Error crítico: WACC <= 0. Revisa los supuestos.")
        return None

    print("\nProyección de FCF y valores presentes:")
    fcf = fcf_actual
    vp_fcfs = []
    for i, g in enumerate(crecimientos, start=1):
        fcf *= (1 + g / 100)
        vp = fcf / ((1 + wacc) ** i)
        vp_fcfs.append(vp)
        print(f"Año {i} - FCF: {fcf:.2f} | VP: {vp:.2f}")

    valor_terminal = (fcf * (1 + g_terminal)) / (wacc - g_terminal)
    vp_valor_terminal = valor_terminal / ((1 + wacc) ** 5)
    ev = sum(vp_fcfs) + vp_valor_terminal

    deuda_neta = deuda - caja
    equity = ev - deuda_neta
    if numero_acciones == 0:
        print("No se puede calcular Precio teórico por acción: divisor 0.")
        return None
    precio_teorico = equity / numero_acciones

    peso_terminal = vp_valor_terminal / ev if ev != 0 else 0
    if peso_terminal > 0.70:
        print("Advertencia: el valor terminal representa >70% del EV total.")

    print(f"Valor terminal: {valor_terminal:.2f}")
    print(f"VP del valor terminal: {vp_valor_terminal:.2f}")
    print(f"Peso del valor terminal en EV: {peso_terminal:.2%}")
    print(f"Valor empresa total (EV): {ev:.2f}")
    print(f"Valor del equity: {equity:.2f}")
    print(f"Precio teórico por acción: {precio_teorico:.2f}")

    if precio_mercado > 0:
        diferencia_pct = (precio_mercado - precio_teorico) / precio_teorico
        print("\nClasificación según precio de mercado (DCF 5 años):")
        if diferencia_pct < -0.20:
            print(
                "Infravalorada: el precio de mercado está >20% por debajo del DCF a 5 años, "
                "lo que indica potencial si el crecimiento se materializa."
            )
        elif diferencia_pct <= 0.20:
            print(
                "Precio razonable: el mercado está dentro de ±20% del DCF a 5 años, "
                "lo que sugiere valoración coherente con la fase de negocio."
            )
        else:
            print(
                "Sobrevalorada: el precio de mercado está >20% por encima del DCF a 5 años, "
                "lo que implica expectativas de crecimiento exigentes."
            )

    return precio_teorico


if __name__ == "__main__":
    resultado = calcular_ratios()
    precio_perpetuo = calcular_dcf_perpetuidad(resultado["precio"], resultado["veredicto"])
    print(
        "\nDCF por proyección explícita (5 años + valor terminal): "
        "útil para empresas growth o en transición."
    )
    precio_proyeccion = calcular_dcf_proyeccion(resultado["precio"])

    if precio_perpetuo is not None and precio_proyeccion is not None:
        print("\nComparación entre modelos DCF:")
        if precio_proyeccion < precio_perpetuo:
            print(
                "El DCF por proyección arroja un valor inferior al perpetuo debido a "
                "una desaceleración prevista del crecimiento y/o mayor riesgo en el corto plazo."
            )
        elif precio_proyeccion > precio_perpetuo:
            print(
                "El DCF por proyección arroja un valor superior al perpetuo, lo que refleja "
                "una fase de crecimiento más intensa antes de la madurez."
            )
        else:
            print("Ambos DCF son coherentes, sugiriendo supuestos de crecimiento similares.")
