"""Mini app web de análisis financiero (MVP) con Streamlit."""

import streamlit as st

from analysis import ejecutar_analisis


st.set_page_config(page_title="Análisis Financiero MVP", layout="wide")
st.title("📊 Mini App de Análisis Financiero")
st.caption("Ratios + DCF perpetuo + DCF 5 años + Investment Score")

# Interfaz en dos columnas para mantener diseño limpio.
col1, col2 = st.columns(2)

with col1:
    st.subheader("Datos de empresa")
    tipo_empresa = st.selectbox("Tipo de empresa", ["growth", "madura", "defensiva", "cíclica"])
    ingresos = st.number_input("Ingresos", min_value=0.0, value=1000.0, step=10.0)
    ebitda = st.number_input("EBITDA", value=200.0, step=10.0)
    fcf = st.number_input("FCF actual", value=120.0, step=10.0)
    deuda = st.number_input("Deuda total", min_value=0.0, value=300.0, step=10.0)
    caja = st.number_input("Caja disponible", min_value=0.0, value=100.0, step=10.0)
    precio_accion = st.number_input("Precio de la acción", min_value=0.0, value=20.0, step=0.5)
    numero_acciones = st.number_input("Número de acciones", min_value=0.0, value=100.0, step=1.0)
    patrimonio_neto = st.number_input("Patrimonio neto", value=500.0, step=10.0)
    activos_totales = st.number_input("Activos totales", value=1500.0, step=10.0)
    beneficio_neto = st.number_input("Beneficio neto", value=80.0, step=10.0)

with col2:
    st.subheader("Supuestos DCF")
    st.markdown("**DCF perpetuo (escenarios de crecimiento)**")
    g_conservador_pct = st.number_input("g conservador (%)", value=1.5, step=0.1)
    g_base_pct = st.number_input("g base (%)", value=2.0, step=0.1)
    g_optimista_pct = st.number_input("g optimista (%)", value=2.5, step=0.1)

    st.markdown("**DCF por proyección (5 años + terminal)**")
    g_inicial_pct = st.number_input("Crecimiento inicial (%)", value=10.0, step=0.5)
    g_terminal_pct = st.number_input("Crecimiento terminal (%)", value=2.0, step=0.1)

if st.button("Analizar empresa", type="primary"):
    # Validaciones de coherencia de input.
    errores = []
    if numero_acciones <= 0:
        errores.append("El número de acciones debe ser mayor que 0.")
    if precio_accion <= 0:
        errores.append("El precio de la acción debe ser mayor que 0.")
    if g_terminal_pct > g_inicial_pct:
        errores.append("El crecimiento terminal no debe superar al crecimiento inicial para la senda decreciente.")

    if errores:
        for e in errores:
            st.error(e)
        st.stop()

    datos = {
        "tipo_empresa": tipo_empresa,
        "ingresos": ingresos,
        "ebitda": ebitda,
        "fcf": fcf,
        "deuda": deuda,
        "caja": caja,
        "precio_accion": precio_accion,
        "numero_acciones": numero_acciones,
        "patrimonio_neto": patrimonio_neto,
        "activos_totales": activos_totales,
        "beneficio_neto": beneficio_neto,
        "g_conservador_pct": g_conservador_pct,
        "g_base_pct": g_base_pct,
        "g_optimista_pct": g_optimista_pct,
        "g_inicial_pct": g_inicial_pct,
        "g_terminal_pct": g_terminal_pct,
    }

    resultado = ejecutar_analisis(datos)

    st.subheader("WACC automático")
    st.write(f"**WACC final:** {resultado['wacc_info']['wacc'] * 100:.2f}%")
    for j in resultado["wacc_info"]["justificacion"]:
        st.write(f"- {j}")

    st.subheader("Tabla de ratios")
    ratios_table = []
    for nombre, valor in resultado["ratios_info"]["ratios"].items():
        ratios_table.append({
            "Ratio": nombre,
            "Valor": "N/A" if valor is None else f"{valor:.2f}",
        })
    st.table(ratios_table)

    st.subheader("DCF perpetuo")
    dcf_perpetuo_rows = []
    for esc, info in resultado["dcf_perpetuo"]["escenarios"].items():
        if "error" in info:
            dcf_perpetuo_rows.append({"Escenario": esc, "Error": info["error"]})
        else:
            dcf_perpetuo_rows.append(
                {
                    "Escenario": esc,
                    "WACC (%)": f"{info['wacc'] * 100:.2f}",
                    "g (%)": f"{info['g'] * 100:.2f}",
                    "Valor empresa": f"{info['valor_empresa']:.2f}",
                    "Valor equity": f"{info['valor_equity']:.2f}",
                    "Precio teórico": f"{info['precio']:.2f}",
                }
            )
    st.table(dcf_perpetuo_rows)

    st.subheader("DCF por proyección (5 años)")
    dcf_proj = resultado["dcf_proyeccion"]
    if "error" in dcf_proj:
        st.error(dcf_proj["error"])
    else:
        tabla_g = []
        for i, g in enumerate(dcf_proj["crecimientos_pct"], start=1):
            tabla_g.append({"Año": i, "g (%)": f"{g:.2f}"})
        st.write("**Crecimientos automáticos usados**")
        st.table(tabla_g)

        tabla_fcf = []
        for i, (fcf_t, vp_t) in enumerate(zip(dcf_proj["fcf_proyectados"], dcf_proj["vp_fcfs"]), start=1):
            tabla_fcf.append(
                {"Año": i, "FCF proyectado": f"{fcf_t:.2f}", "VP(FCF)": f"{vp_t:.2f}"}
            )
        st.table(tabla_fcf)

        st.write(f"**Valor terminal:** {dcf_proj['valor_terminal']:.2f}")
        st.write(f"**VP valor terminal:** {dcf_proj['vp_terminal']:.2f}")
        st.write(f"**Peso terminal en EV:** {dcf_proj['peso_terminal']:.2%}")
        st.write(f"**Valor empresa (EV):** {dcf_proj['ev']:.2f}")
        st.write(f"**Valor equity:** {dcf_proj['equity']:.2f}")
        st.write(f"**Precio teórico por acción:** {dcf_proj['precio']:.2f}")

    st.subheader("Precio teórico vs mercado")
    precio_base = resultado["dcf_perpetuo"]["precio_base"]
    precio_proj = resultado["dcf_proyeccion"].get("precio") if isinstance(resultado["dcf_proyeccion"], dict) else None
    comparativa = [
        {"Métrica": "Precio mercado", "Valor": f"{datos['precio_accion']:.2f}"},
        {"Métrica": "Precio DCF perpetuo (base)", "Valor": "N/A" if precio_base is None else f"{precio_base:.2f}"},
        {"Métrica": "Precio DCF proyección", "Valor": "N/A" if precio_proj is None else f"{precio_proj:.2f}"},
    ]
    st.table(comparativa)

    st.subheader("Investment Score")
    score = resultado["score"]
    st.write(f"**Score total:** {score['total']:.0f}/100")
    st.write(f"**Clasificación final:** {score['clasificacion']}")
    st.table(
        [
            {"Bloque": "Valoración", "Puntos": f"{score['valoracion']:.0f}/40"},
            {"Bloque": "Rentabilidad", "Puntos": f"{score['rentabilidad']:.0f}/25"},
            {"Bloque": "Riesgo financiero", "Puntos": f"{score['riesgo']:.0f}/20"},
            {"Bloque": "DCF vs mercado", "Puntos": f"{score['dcf_vs_mercado']:.0f}/15"},
        ]
    )

    st.subheader("Veredicto cualitativo y advertencias")
    st.write(f"**Veredicto preliminar (ratios):** {resultado['ratios_info']['veredicto_preliminar']}")
    if resultado["comparacion_dcf"]:
        st.info(resultado["comparacion_dcf"])

    advertencias = (
        resultado["ratios_info"]["advertencias"]
        + resultado["dcf_perpetuo"]["advertencias"]
        + resultado["dcf_proyeccion"].get("advertencias", [])
    )
    if advertencias:
        for a in advertencias:
            st.warning(a)
    else:
        st.success("Sin advertencias críticas con los supuestos actuales.")
