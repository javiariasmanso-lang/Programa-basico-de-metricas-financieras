# Programa-basico-de-metricas-financieras

Mini app de análisis de inversión con:
- ratios financieros
- DCF perpetuo (control)
- DCF por proyección a 5 años + valor terminal
- investment score final

## Estructura

- `analysis.py`: lógica financiera (fórmulas, reglas y validaciones)
- `app.py`: interfaz web con Streamlit

## Uso (MVP local)

```bash
streamlit run app.py
```

## Nota

Se mantiene `main.py` como versión CLI previa, pero la interfaz recomendada para el MVP es Streamlit.
