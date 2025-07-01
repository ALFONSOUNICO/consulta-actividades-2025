# Reescribimos el archivo app.py sin usar fpdf para evitar errores de importación
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from urllib.parse import quote
from collections import Counter
import re
import io

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
        "monthly_summary": "🧠 Resumen mensual",
        "filter_tags": "Filtrar por etiquetas frecuentes",
        "kpi_total": "Total de atenciones",
        "kpi_avg_week": "Promedio semanal",
        "kpi_max_day": "Día con más actividad",
        "calendar": "📅 Calendario de actividad",
        "alerts": "🔔 Alertas"
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
        "monthly_summary": "🧠 Monthly summary",
        "filter_tags": "Filter by frequent tags",
        "kpi_total": "Total attentions",
        "kpi_avg_week": "Weekly average",
        "kpi_max_day": "Day with most activity",
        "calendar": "📅 Activity calendar",
        "alerts": "🔔 Alerts"
    }
}

t = texts[lang]

st.set_page_config(page_title=t["title"], layout="wide")
st.title(t["title"])

st.image("banner.png", use_container_width=True)

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

# Generar etiquetas frecuentes
text_data = df['atencion'].fillna('') + ' ' + df['solucion'].fillna('')
words = re.findall(r'\b\w{4,}\b', ' '.join(text_data).lower())
word_counts = Counter(words)
top_keywords = [word for word, count in word_counts.most_common(30)]

def etiquetar_fila(texto, etiquetas):
    texto = texto.lower()
    return [etiqueta for etiqueta in etiquetas if etiqueta in texto]

df['etiquetas'] = text_data.apply(lambda x: etiquetar_fila(x, top_keywords))
etiquetas_unicas = sorted(set(etiqueta for lista in df['etiquetas'] for etiqueta in lista))

# Filtros
st.sidebar.header("🔍 Filtros")
fecha_inicio = st.sidebar.date_input(t["date_start"], value=pd.to_datetime("2025-01-01"))
fecha_fin = st.sidebar.date_input(t["date_end"], value=pd.to_datetime("2025-12-31"))
palabra_atencion = st.sidebar.text_input(t["search_attention"])
palabra_solucion = st.sidebar.text_input(t["search_solution"])
etiqueta_seleccionada = st.sidebar.multiselect(t["filter_tags"], options=etiquetas_unicas)

# Aplicar filtros
df_filtrado = df[
    (df['fecha'] >= pd.to_datetime(fecha_inicio)) &
    (df['fecha'] <= pd.to_datetime(fecha_fin))
]

if palabra_atencion:
    df_filtrado = df_filtrado[df_filtrado['atencion'].str.contains(palabra_atencion, case=False, na=False)]

if palabra_solucion:
    df_filtrado = df_filtrado[df_filtrado['solucion'].str.contains(palabra_solucion, case=False, na=False)]

if etiqueta_seleccionada:
    df_filtrado = df_filtrado[df_filtrado['etiquetas'].apply(lambda etiquetas: any(e in etiquetas for e in etiqueta_seleccionada))]

# KPIs
st.subheader("📊 KPIs")
col1, col2, col3 = st.columns(3)
total = len(df_filtrado)
promedio = df_filtrado.groupby(df_filtrado['fecha'].dt.to_period('W')).size().mean()
if not df_filtrado.empty:
    dia_max = df_filtrado['fecha'].value_counts().idxmax().strftime("%Y-%m-%d")
else:
    dia_max = "-"
col1.metric(t["kpi_total"], total)
col2.metric(t["kpi_avg_week"], round(promedio, 2) if not pd.isna(promedio) else 0)
col3.metric(t["kpi_max_day"], dia_max)

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

# Visualizaciones
if not df_filtrado.empty:
    st.subheader(t["timeline"])
    timeline = df_filtrado.groupby('fecha').size().reset_index(name='conteo')
    fig_timeline = px.line(timeline, x='fecha', y='conteo', markers=True)
    st.plotly_chart(fig_timeline, use_container_width=True)

    st.subheader(t["monthly"])
    df_filtrado['mes'] = df_filtrado['fecha'].dt.to_period('M').astype(str)
    mensual = df_filtrado.groupby('mes').size().reset_index(name='conteo')
    fig_mensual = px.bar(mensual, x='mes', y='conteo')
    st.plotly_chart(fig_mensual, use_container_width=True)

    st.subheader(t["weekly_summary"])
    df_filtrado['semana'] = df_filtrado['fecha'].dt.to_period('W').astype(str)
    resumen_semana = df_filtrado.groupby('semana').size().reset_index(name='conteo')
    st.dataframe(resumen_semana)

    st.subheader(t["monthly_summary"])
    resumen_mes = df_filtrado.groupby('mes').size().reset_index(name='conteo')
    st.dataframe(resumen_mes)

    # Calendario tipo heatmap
    st.subheader(t["calendar"])
    calendar_data = df_filtrado.groupby('fecha').size()
    calendar_df = calendar_data.reset_index()
    calendar_df.columns = ['fecha', 'conteo']
    calendar_df['fecha'] = pd.to_datetime(calendar_df['fecha'])
    calendar_df['day'] = calendar_df['fecha'].dt.date
    calendar_df.set_index('day', inplace=True)
    fig, ax = plt.subplots(figsize=(12, 2))
    sns.heatmap(calendar_df[['conteo']].T, cmap="YlGnBu", cbar=True, ax=ax)
    st.pyplot(fig)

    # Alertas
    st.subheader(t["alerts"])
    full_range = pd.date_range(start=fecha_inicio, end=fecha_fin)
    dias_sin_actividad = sorted(set(full_range.date) - set(df_filtrado['fecha'].dt.date))
    if dias_sin_actividad:
        st.warning(f"{len(dias_sin_actividad)} días sin actividad detectados.")

    conteo_dias = df_filtrado['fecha'].value_counts()
    media = conteo_dias.mean()
    std = conteo_dias.std()
    dias_pico = conteo_dias[conteo_dias > media + 2 * std].index.strftime("%Y-%m-%d").tolist()
    if dias_pico:
        st.error(f"Picos inusuales detectados en: {', '.join(dias_pico)}")

