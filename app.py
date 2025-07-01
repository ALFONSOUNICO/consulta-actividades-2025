import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import quote

# Configuración de idioma
lang = st.sidebar.selectbox("🌐 Language / Idioma", ["Español", "English"])

# Traducciones básicas
texts = {
    "Español": {
        "title": "Consulta de Actividades 2025",
        "date_start": "Fecha inicio",
        "date_end": "Fecha fin",
        "search_attention": "Buscar en Atención",
        "search_solution": "Buscar en Solución",
        "results": "Resultados de la consulta",
        "download": "Descargar resultados como CSV",
        "timeline": "📈 Línea de tiempo de atenciones",
        "monthly": "📊 Atenciones por mes",
        "weekly_summary": "🧠 Resumen semanal",
        "monthly_summary": "🧠 Resumen mensual"
    },
    "English": {
        "title": "2025 Activities Query",
        "date_start": "Start date",
        "date_end": "End date",
        "search_attention": "Search in Attention",
        "search_solution": "Search in Solution",
        "results": "Query results",
        "download": "Download results as CSV",
        "timeline": "📈 Attention timeline",
        "monthly": "📊 Monthly attentions",
        "weekly_summary": "🧠 Weekly summary",
        "monthly_summary": "🧠 Monthly summary"
    }
}

t = texts[lang]

st.set_page_config(page_title=t["title"], layout="wide")
st.title(t["title"])

# Leer datos desde Google Sheets
sheet_id = "10rYgKcSGsMTq2F2-vh0SxWQNIQ7OVjKS"
sheet_name = "Enero 2025"
encoded_sheet_name = quote(sheet_name)
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    df.columns = [col.strip().lower() for col in df.columns]
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce', dayfirst=True)
    return df

df = load_data(url)

# Filtros
st.sidebar.header("🔍 Filtros")
fecha_inicio = st.sidebar.date_input(t["date_start"], value=pd.to_datetime("2025-01-01"))
fecha_fin = st.sidebar.date_input(t["date_end"], value=pd.to_datetime("2025-12-31"))
palabra_atencion = st.sidebar.text_input(t["search_attention"])
palabra_solucion = st.sidebar.text_input(t["search_solution"])

# Aplicar filtros
df_filtrado = df[
    (df['fecha'] >= pd.to_datetime(fecha_inicio)) &
    (df['fecha'] <= pd.to_datetime(fecha_fin))
]

if palabra_atencion:
    df_filtrado = df_filtrado[df_filtrado['atencion'].str.contains(palabra_atencion, case=False, na=False)]

if palabra_solucion:
    df_filtrado = df_filtrado[df_filtrado['solucion'].str.contains(palabra_solucion, case=False, na=False)]

# Mostrar resultados
st.subheader(t["results"])
st.dataframe(df_filtrado)

# Descargar CSV
@st.cache_data
def convertir_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convertir_csv(df_filtrado)
st.download_button(
    label=t["download"],
    data=csv,
    file_name='resultados_filtrados.csv',
    mime='text/csv',
)

# Gráfico de línea de tiempo
if not df_filtrado.empty:
    st.subheader(t["timeline"])
    timeline = df_filtrado.groupby('fecha').size().reset_index(name='conteo')
    fig_timeline = px.line(timeline, x='fecha', y='conteo', markers=True)
    st.plotly_chart(fig_timeline, use_container_width=True)

    # Gráfico mensual
    st.subheader(t["monthly"])
    df_filtrado['mes'] = df_filtrado['fecha'].dt.to_period('M').astype(str)
    mensual = df_filtrado.groupby('mes').size().reset_index(name='conteo')
    fig_mensual = px.bar(mensual, x='mes', y='conteo')
    st.plotly_chart(fig_mensual, use_container_width=True)

    # Resumen semanal
    st.subheader(t["weekly_summary"])
    df_filtrado['semana'] = df_filtrado['fecha'].dt.to_period('W').astype(str)
    resumen_semana = df_filtrado.groupby('semana').size().reset_index(name='conteo')
    st.dataframe(resumen_semana)

    # Resumen mensual
    st.subheader(t["monthly_summary"])
    resumen_mes = df_filtrado.groupby('mes').size().reset_index(name='conteo')
    st.dataframe(resumen_mes)

