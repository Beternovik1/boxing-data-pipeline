import streamlit as st # Framework para crear una web app
import pandas as pd
from pymongo import MongoClient # Para hablar con la base de datos en la nube
import plotly.express as px # Para hacer los graficos
import os # Para buscar las contrasenas en el sistema

# Configuracion de la pagina
# Configuramos el titulo de la pestana del navegador 
# y ponemos como icono un guante
st.set_page_config(page_title="Boxing Dashboard", page_icon="🥊", layout="wide")

# @st.cache_resource es un "Decorador".
# Le dice a Streamlit: "Ejecuta esta funcion una sola vez
# y guarda la conexion en memoria".
# Si no se usa cada vez que alguien entre a la web python 
# se reconectaria a Mongo desde cero y alentaria mucho la pagina.
@st.cache_resource
def init_connection():
    # Intenta leer el secreto de las variables de entorno 
    uri = os.environ.get("MONGO_URI")

    if not uri:
        uri = "mongodb+srv://edgaralfarohernandez15_db_user:ICN30t2E4rZPcxKt@cluster0.lueezcu.mongodb.net/?appName=Cluster0"
        
    return MongoClient(uri)

# Guardamos la conexion activa en la variable  'client'
client = init_connection()

def get_data():
    # Seleccionamos la base de datos y la coleccion
    db = client["campeones_mundiales"]
    col = db["Campeones"]

    # .find() trae todos los documentos.
    # {"_id": 0} es un filtro que trae todo excepto los campos '_id'
    items = list(col.find({}, {"_id":0}))

    # Convertimos la lista de diccionarios en un DF 
    return pd.DataFrame(items)

# Titulo principal
st.title("Dashboard de Campeones Mundiales")
st.markdown("### Analisis en tiempo real de la WBA, WBC, IBF y WBO")

# Llamamos a la funcion get_data para llenar la variable df con datos reales
df = get_data()

# SECCION DE METRICAS (KPIs) 
# st.columns(3) divide la pantalla en 3 columnas invisibles
col1, col2, col3 = st.columns(3)

# Metrica 1: Cuantas filas tiene el DF (total de categorias)
col1.metric("Categorias de Peso", len(df))

# Metrica 2: Dato fijo
col2.metric("Organizaciones", "4 (WBA, WBC, IBF, WBO)")

# Metrica 3: Calculo complejo
# Buscamos la palabra "vacant" en todo el DF y contamos cuantas hay.
total_vacantes = df.apply(lambda x: x.astype(str).str.contains('vacant', case=False).sum(), axis=1).sum()
col3.metric("Titulos Vacantes", total_vacantes)

# Linea divisoria visual
st.divider()

# st.sidebar pone cosas en la barra lateral izquierda
st.sidebar.header("Filtros")

# Obtenermos la lista unica de categorias (Heavyweight, Welter, etc.) para el menu
categorias = df["Category"].unique()

# selectbox crea un menu desplegable.
# Lo que el usuario elija se guarda INSTANTANEAMENTE en la variable 'categoria_seleccionada'
categoria_seleccionada = st.sidebar.selectbox("Selecciona una Categoria:", categorias)

# Mostrar tabla filtrada
st.subheader(f"Campeones en : {categoria_seleccionada}")

# Filtro de Pandas: Dame las filas donde la columna Category sea igual a lo que eligio el usuario
df_filtrado = df[df["Category"] == categoria_seleccionada]

# Pintamos la tabla. hide_index=True quita los numeros de fila (0, 1, 2...)
st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

## GRAFICA DE BARRAS
st.divider()
st.subheader("Titulos Vacantes por Organizacion")

# PReparamos los datos para la grafica
# Contamos manuamente cuandtos "Vacant" tiene cada columna (WBA, WBC, WBO, IBF)
conteo = {
    "WBA": df["WBA"].str.contains("vacant", case=False).sum(),
    "WBC": df["WBC"].str.contains("vacant", case=False).sum(),
    "IBF": df["IBF"].str.contains("vacant", case=False).sum(),
    "WBO": df["WBO"].str.contains("vacant", case=False).sum(),
}

# Convertimos ese diccionario en un mini DF para graficar
df_grafica = pd.DataFrame(list(conteo.items()), columns=["Organizacion", "Vacantes"])

# Usamos Plotly Express (px) para crear la barra
fig = px.bar(
    df_grafica,
    x="Organizacion",
    y="Vacantes",
    color="Organizacion",
    text="Vacantes",
    template="plotly_dark" # Modo oscuro jeje
)

# Mostrando la grafica
st.plotly_chart(fig, use_container_width=True)