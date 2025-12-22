![Build Status](https://github.com/Beternovik1/boxing-data-pipeline/actions/workflows/automatizacion.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat&logo=python)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?style=flat&logo=mongodb)

This project is an automated **ETL Pipeline (Extract, Transform, Load)** that extracts updated information every Sunday at 8:00 AM from Wikipedia regarding world boxing champions from the four major organizations (WBA, WBO, WBC, IBF). It uses GitHub Actions for automation, cleans the data, and stores it in a cloud-based NoSQL database (MongoDB Atlas).

## Project Overview
It solves the problem of collecting and centralizing data on world champion boxers across all weight divisions into a single, up-to-date database.

1.  **Extract:** A bot visits Wikipedia and downloads the HTML tables containing current champions.
2.  **Transform:** Using `pandas`, the data is cleaned by removing junk characters (via Regex) and irrelevant tables. Weight categories are standardized, and information from all tables is consolidated into a single, clean JSON structure.
3.  **Load:** Once processed, the data is injected into a MongoDB Atlas cluster for cloud storage.
4.  **Automation:** Using a CI/CD workflow in GitHub Actions, the script is scheduled to run automatically every Sunday at 8:00 AM.

## Tech Stack
* **Language:** Python 3.10
* **Libraries:**
    * `pandas`: For data manipulation and cleaning (DataFrames).
    * `requests` and `lxml`: For Web Scraping.
    * `pymongo`: For the NoSQL database connection.
    * `streamlit`: For the NoSQL database connection.
    * `plotly`: For building the graphs.

* **Infrastructure:**
    * **GitHub Actions:** For script automation/scheduling.
    * **MongoDB Atlas:** For cloud database hosting.

## Project Structure
```text
BOXING-DATA-PIPELINE/
├── .github/workflows/   # Automation workflow configuration
│   └── automatizacion.yml
├── main.py              # Main ETL Script
├── dashboard.py         # Source code for the Streamlit Web Dashboard
├── requirements.txt     # List of dependencies
└── README.md            # Documentation
