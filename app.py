import re
from collections import Counter

# Unificamos el texto de atención y solución
text_data = datos['atencion'].fillna('') + ' ' + datos['solucion'].fillna('')

# Extraemos palabras frecuentes (mínimo 4 letras)
words = re.findall(r'\b\w{4,}\b', ' '.join(text_data).lower())
word_counts = Counter(words)

# Seleccionamos las 30 palabras más comunes como etiquetas
top_keywords = [word for word, count in word_counts.most_common(30)]

# Función para etiquetar cada fila
def etiquetar_fila(texto, etiquetas):
    texto = texto.lower()
    return [etiqueta for etiqueta in etiquetas if etiqueta in texto]

# Aplicamos etiquetas a cada fila
datos['etiquetas'] = text_data.apply(lambda x: etiquetar_fila(x, top_keywords))

# Lista única de etiquetas
etiquetas_unicas = sorted(set(etiqueta for lista in datos['etiquetas'] for etiqueta in lista))

# Agregamos filtro por etiquetas en la barra lateral
etiqueta_seleccionada = st.sidebar.multiselect("Filtrar por etiquetas frecuentes", opciones := etiquetas_unicas)

# Aplicamos filtro por etiquetas si se seleccionan
if etiqueta_seleccionada:
    datos = datos[datos['etiquetas'].apply(lambda etiquetas: any(e in etiquetas for e in etiqueta_seleccionada))]
