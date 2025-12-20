![Build Status](https://github.com/Beternovik1/boxing-data-pipeline/actions/workflows/automatizacion.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat&logo=python)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?style=flat&logo=mongodb)

El proyecto es un Pipeline ETL (Extract, Transform, Load)** automatizado que extrae información actualizada cada domingo a las 8:00 a. m. de Wikipedia sobre los campeones mundiales de las 4 principales organizaciones mundiales de boxeo (WBA, WBO, WBC, IBF) mediante GitHub Actions, la limpia y almacena en una base de datos NoSQL (MongoDB) en la nube.

## ¿Qué hace el proyecto?
Resuelve la problemática de recopilar la información en una base de datos de los boxeadores campeones del mundo de cada división en su categoría.

1. **Extracción (Extract):** Un bot visita Wikipedia y descarga las tablas HTML de los campeones actuales.
2. **Transformación (Transform):** Mediante 'Pandas', se limpian los datos, eliminando caracteres basura (Regex) y las tablas inservibles, estandarizando las categorías de peso y se recopila la información de todas las tablas en una sola estructura JSON limpia.
3. **Carga (Load):** Una vez tenemos los datos procesados procedemos a inyectarlos en un clúster de MongoDB Atlas para tenerlos en la nube.
4. **Automatización (Automation):** Mediante un flujo CI/CD en GitHub Actions hacemos que el script se ejecute todos los domingos a las 8:00 AM.

## Tecnologías utilizadas
* **Lenguaje:** Python 3.10
* **Librerías:** * 'pandas': Para la manipulación y limpieza de los dataframes.
    * 'requests' y 'lxml': Para hacer el Web Scraping.
    * 'pymongo': Para la conexión con la base de datos NoSQL.
* **Infraestructura:**
    * **GitHub Actions:** Para la automatización del script.
    * **MongoDB Atlas:** Para subir la base de datos a la nube.

## Estructura del Proyecto
```text
BOXING-DATA-PIPELINE/
├── .github/workflows/   # Configuración de la automatización del script.
│   └── automatizacion.yml
├── main.py              # Código del ETL
├── requirements.txt     # Lista de librerías
└── README.md            # Documentación