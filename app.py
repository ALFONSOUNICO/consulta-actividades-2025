import streamlit as st
import pandas as pd

st.title("Consulta de Actividades 2025")

# Leer desde Google Sheets
sheet_id = "10rYgKcSGsMTq2F2-vh0SxWQNIQ7OVjKS"  # Reemplaza con tu ID real si cambia
sheet_name = "Enero"  # Cambia por el nombre de la hoja que deseas consultar
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# Cargar datos desde Google Sheets
datos = pd.read_csv(url)
datos.columns = [col.strip().lower() for col in datos.columns]
datos['fecha'] = pd.to_datetime(datos['fecha'], errors='coerce', dayfirst=True)

# Filtros de búsqueda
st.sidebar.header("Filtros de búsqueda")
fecha_inicio = st.sidebar.date_input("Fecha inicio", value=pd.to_datetime("2025-01-01"))
fecha_fin = st.sidebar.date_input("Fecha fin", value=pd.to_datetime("2025-12-31"))
palabra_atencion = st.sidebar.text_input("Buscar en Atencion")
palabra_solucion = st.sidebar.text_input("Buscar en Solucion")

# Aplicar filtros
datos_filtrados = datos[
    (datos['fecha'] >= pd.to_datetime(fecha_inicio)) &
    (datos['fecha'] <= pd.to_datetime(fecha_fin))
]

if palabra_atencion:
    datos_filtrados = datos_filtrados[datos_filtrados['atencion'].str.contains(palabra_atencion, case=False, na=False)]

if palabra_solucion:
    datos_filtrados = datos_filtrados[datos_filtrados['solucion'].str.contains(palabra_solucion, case=False, na=False)]

# Mostrar resultados
st.subheader("Resultados de la consulta")
st.dataframe(datos_filtrados)

# Función para exportar CSV
@st.cache_data
def convertir_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convertir_csv(datos_filtrados)
st.download_button(
    label="Descargar resultados como CSV",
    data=csv,
    file_name='resultados_filtrados.csv',
    mime='text/csv',
)
