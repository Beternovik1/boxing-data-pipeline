# --------------------------------------- ETL --------------------------------------------------
# 1. LIBRERIAS
import pandas as pd
# Libreria para acceder al codigo HTTML de una pagina WEB, lo devuelve como un String gigante
import requests 
# Toma el texto gigante y lo envuelve para que parezca un archivo en memoria y pandas lo pueda leer
from io import StringIO
# Es el cable que conecta mongodb con python
from pymongo import MongoClient

# 2. CONSTANTES
URL = "https://en.wikipedia.org/wiki/List_of_current_world_boxing_champions"

# -------------------------------------- EXTRACTING ---------------------------------------------
# 3. FUNCION DE EXTRACCION DE LA INFORMACION
def extract_champions():
    print(f"Conectando a {URL}")

    # Web scrapping (disfraz) fingimos ser una persona normal usando Google Chrome en Windows 10 para 
    # acceder a wikipedia y no nos nieguen el acceso
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"        
    }

    try:
        # A. Haciendo la peticion GET a wikipedia
        response = requests.get(URL, headers = headers)

        # Verificando que tengamos acceso a la informacion con el status_code 200
        # Si fuera 404: "No existe esa página".
        # Si fuera 403: "Prohibido el paso (te caché que eres un robot)".
        # Si fuera 500: "El servidor de Wikipedia se incendió".
        if response.status_code == 200:
            print("Descargando tablas...")

            # B. Leeyendo el HTML
            # Filtrando las tablas de boxeo donde aparezca la palabra clave "WBA"
            # pd.read_html busca especificamente tablas (<table></table)
            todas_las_tablas = pd.read_html(StringIO(response.text), match="WBA")

            print(f"Hay {len(todas_las_tablas)} tablas.")

            # Regresando la lista completa con todas las tablas buenas
            return todas_las_tablas
        else:
            print(f'Error de conexion {response.status_code}')
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []
    
# -------------------------------------- TRANSFORMING ---------------------------------------------
def transform_data(lista_de_tablas):
    # A. Slicing de nuestra lista de tablas para descartar las ultimas 2 tablas que no nos sirven
    lista_limpia = lista_de_tablas[:18]

    # B. Agregando una columna a cada tabla para indicar la categoria de peso
    # Categorias de mayor a menor peso
    categorias = [
        "Heavyweight", "Bridgerweight", "Cruiserweight", "Light heavyweight", 
        "Super middleweight", "Middleweight", "Super welterweight", "Welterweight", 
        "Super lightweight", "Lightweight", "Super featherweight", "Featherweight", 
        "Super bantamweight", "Bantamweight", "Super flyweight", "Flyweight", 
        "Light flyweight", "Minimumweight"
    ]

    for i in range(len(lista_limpia)):
        lista_limpia[i]["Category"] = categorias[i]

    # C. Uniendo todas las tablas en un solo DF
    df_final = pd.concat(lista_limpia, ignore_index=True)
    
    # D. Limpiando el texto usando Regex (Expresiones Regulares)
    # Explicación del regex '\[.*\]|\(.*\)':
    # \[.*\]  -> Busca corchetes y todo lo que tengan dentro (ej: [15])
    # |       -> O (OR)
    # \(.*\)  -> Busca paréntesis y todo lo que tengan dentro (ej: (Super champion))
    # Remplazamos todo eso por "" en el DF
    df_final = df_final.replace(to_replace=r'\[.*\]|\(.*\)', value='', regex=True)

    # E. Renombramos las columnas 
    df_final.columns = ["WBA", "WBC", "IBF", "WBO", "The_Ring", "Category"]

    # F. Quitando filas basura
    df_final = df_final[df_final["WBA"] != "WBA"]
    return df_final 

# -------------------------------------- LOADING ---------------------------------------------
def load_data(df_final):
    print("Cargando los datos a MongoDB...")

    # A. Conexion al cliente
    uri = "mongodb+srv://edgaralfarohernandez15_db_user:ICN30t2E4rZPcxKt@cluster0.lueezcu.mongodb.net/?appName=Cluster0"
    cliente = MongoClient(uri)

    # B. Traduciendo los DF a diccionarios para MongoDB
    # orient='records' es porque queremos que cada fila de las tablas
    # se convierta a un objeto individual {}
    lista_diccionarios = df_final.to_dict(orient='records')

    # C. Definiendo la bd
    # Definiendo el nombre para la bd
    db = cliente["campeones_mundiales"]
    col = db["Campeones"]
    # Limbiarmos la coleccion antes de meter datos nuevos
    # para no duplicar
    col.delete_many({})
    col.insert_many(lista_diccionarios)

    print("Datos cargados exitosamente en la Nube !!!! ")
    return db

# ----------------------------------- CLOUD FUNCTION ENTRY POINT ---------------------------------------------
def ejecutar_pipeline(request):
    print("Iniciando pipeline desde Google Cloud...")
    try:
        # 1. Extraccion
        mis_tablas = extract_champions()

        if len(mis_tablas) > 0:
            # 2. Transformacion
            df_final = transform_data(mis_tablas)
            # 3. Carga
            load_data(df_final)
            return "Pipeline ejecutado correctamente" , 200
        else:
            return "Error: No se encontraron las tablas en Wikipedia.", 500
    except Exception as e:
        print(f'Error critico: {e}')
        return f'Ocurrio un error en el servidor: {str(e)}', 500

# ---------------------------------------- PRUEBA LOCAL ---------------------------------------------
if __name__ == "__main__":
    print("--- Modo local ----")
    ejecutar_pipeline(None)





# Creando un entorno virtual
# python -m venv venv

# Activar el entorno virtual
# source venv/Scripts/activate

# Comando para despertar docker
# docker start mi-mongo