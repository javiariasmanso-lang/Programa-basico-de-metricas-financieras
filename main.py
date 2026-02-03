"""Programa básico de métricas financieras."""


def calcular_ratios():
    """Solicita datos financieros y calcula ratios básicos."""
    ingresos = float(input("Ingresos: "))
    ebitda = float(input("EBITDA: "))
    fcf = float(input("FCF: "))
    deuda_neta = float(input("Deuda neta: "))
    precio_accion = float(input("Precio de la acción: "))
    numero_acciones = float(input("Número de acciones: "))
    patrimonio_neto = float(input("Patrimonio neto: "))
    activos_totales = float(input("Activos totales: "))
    beneficio_neto = float(input("Beneficio neto: "))

    # Cálculo de capitalización y valor de empresa (EV)
    capitalizacion = precio_accion * numero_acciones
    ev = capitalizacion + deuda_neta

    print("\nResultados de ratios:")

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
        print("No se puede calcular margen EBITDA: divisor 0")
    else:
        margen_ebitda = ebitda / ingresos
        print(f"Margen EBITDA: {margen_ebitda:.2f}")


def calcular_dcf():
    """Calcula el valor teórico por acción con un modelo DCF perpetuo."""
    fcf_actual = float(input("FCF actual: "))
    g = float(input("g (crecimiento perpetuo): "))
    wacc = float(input("WACC: "))
    deuda_neta = float(input("Deuda neta: "))
    numero_acciones = float(input("Número de acciones: "))

    print("\nResultados del DCF:")

    if wacc == g:
        print("No se puede calcular el valor empresa: WACC es igual a g")
        return

    if wacc - g == 0:
        print("No se puede calcular el valor empresa: divisor 0")
        return

    valor_empresa = fcf_actual * (1 + g) / (wacc - g)
    valor_equity = valor_empresa - deuda_neta

    if numero_acciones == 0:
        print("No se puede calcular el precio teórico: divisor 0")
        return

    precio_teorico = valor_equity / numero_acciones

    print(f"Valor empresa: {valor_empresa:.2f}")
    print(f"Valor equity: {valor_equity:.2f}")
    print(f"Precio teórico por acción: {precio_teorico:.2f}")


if __name__ == "__main__":
    calcular_ratios()
    calcular_dcf()
