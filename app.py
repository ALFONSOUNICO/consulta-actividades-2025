import streamlit as st
import pandas as pd

@st.cache_data
def cargar_datos(archivo_excel):
    xls = pd.ExcelFile(archivo_excel, engine='openpyxl')
    df_total = pd.DataFrame()
    for hoja in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=hoja)
        df.columns = [col.strip().lower() for col in df.columns]
        df_total = pd.concat([df_total, df], ignore_index=True)
    df_total['fecha'] = pd.to_datetime(df_total['fecha'], errors='coerce', dayfirst=True)
    return df_total

st.title("Consulta de Actividades 2025")
archivo = st.file_uploader("Sube el archivo Excel de actividades", type=["xlsx"])

if archivo:
    datos = cargar_datos(archivo)

    st.sidebar.header("Filtros de búsqueda")
    fecha_inicio = st.sidebar.date_input("Fecha inicio", value=pd.to_datetime("2025-01-01"))
    fecha_fin = st.sidebar.date_input("Fecha fin", value=pd.to_datetime("2025-12-31"))
    palabra_atencion = st.sidebar.text_input("Buscar en Atencion")
    palabra_solucion = st.sidebar.text_input("Buscar en Solucion")

    datos_filtrados = datos[
        (datos['fecha'] >= pd.to_datetime(fecha_inicio)) &
        (datos['fecha'] <= pd.to_datetime(fecha_fin))
    ]

    if palabra_atencion:
        datos_filtrados = datos_filtrados[datos_filtrados['atencion'].str.contains(palabra_atencion, case=False, na=False)]

    if palabra_solucion:
        datos_filtrados = datos_filtrados[datos_filtrados['solucion'].str.contains(palabra_solucion, case=False, na=False)]

    st.subheader("Resultados de la consulta")
    st.dataframe(datos_filtrados)

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
