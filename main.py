# --------------------------------------- ETL PIPELINE ---------------------------------------
# 1. LIBRARIES
import pandas as pd
import requests 
from io import StringIO
from pymongo import MongoClient
import os

# 2. CONSTANTS
URL = "https://en.wikipedia.org/wiki/List_of_current_world_boxing_champions"

# -------------------------------------- EXTRACTING ---------------------------------------------
def extract_champions():
    print(f"Connecting to {URL}...")

    # Web scraping (User-Agent spoofing): 
    # We pretend to be a normal user on Chrome/Windows 10 so Wikipedia doesn't block the request.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"        
    }

    try:
        # A. Making the GET request
        response = requests.get(URL, headers=headers)

        # Checking status_code 200 (OK)
        # 404: Not Found.
        # 403: Forbidden (Bot detected).
        # 500: Server Error.
        if response.status_code == 200:
            print("Downloading tables...")

            # B. Reading HTML
            # Filtering for boxing tables containing the keyword "WBA"
            # pd.read_html looks specifically for <table> tags
            all_tables = pd.read_html(StringIO(response.text), match="WBA")

            print(f"Found {len(all_tables)} tables.")

            # Return the complete list of valid tables
            return all_tables
        else:
            print(f'Connection error: Status code {response.status_code}')
            return []
    except Exception as e:
        print(f"Error during extraction: {e}")
        return []
    
# -------------------------------------- TRANSFORMING ---------------------------------------------
def transform_data(tables_list):
    # A. Slicing the list to discard the last 2 tables (irrelevant data)
    filtered_tables = tables_list[:18]

    # B. Adding a 'Category' column to each table
    # Weight categories from heaviest to lightest
    categories = [
        "Heavyweight", "Bridgerweight", "Cruiserweight", "Light heavyweight", 
        "Super middleweight", "Middleweight", "Super welterweight", "Welterweight", 
        "Super lightweight", "Lightweight", "Super featherweight", "Featherweight", 
        "Super bantamweight", "Bantamweight", "Super flyweight", "Flyweight", 
        "Light flyweight", "Minimumweight"
    ]

    for i in range(len(filtered_tables)):
        filtered_tables[i]["Category"] = categories[i]

    # C. Merging all tables into a single DataFrame
    final_df = pd.concat(filtered_tables, ignore_index=True)
    
    # D. Cleaning text using Regex (Regular Expressions)
    # Explanation of regex '\[.*\]|\(.*\)':
    # \[.*\]  -> Matches brackets and their content (e.g., [15])
    # |       -> OR
    # \(.*\)  -> Matches parentheses and their content (e.g., (Super champion))
    # We replace matches with an empty string ""
    final_df = final_df.replace(to_replace=r'\[.*\]|\(.*\)', value='', regex=True)

    # E. Renaming columns 
    final_df.columns = ["WBA", "WBC", "IBF", "WBO", "The_Ring", "Category"]

    # F. Removing junk rows (headers repeated inside the data)
    final_df = final_df[final_df["WBA"] != "WBA"]
    
    return final_df 

# -------------------------------------- LOADING ---------------------------------------------
def load_data(final_df):
    print("Loading data into MongoDB...")

    # A. Client Connection
    # We use environment variables for security. 
    # If not found (local dev), fall back to the hardcoded string.
    uri = os.environ.get("MONGO_URI")

    if not uri:
        uri = "mongodb+srv://edgaralfarohernandez15_db_user:ICN30t2E4rZPcxKt@cluster0.lueezcu.mongodb.net/?appName=Cluster0"
    
    client = MongoClient(uri)

    # B. Converting DataFrame to a list of dictionaries (JSON-like format)
    # orient='records' turns each row into an individual object {}
    records_list = final_df.to_dict(orient='records')

    # C. Defining the Database and Collection
    # Note: Keeping original DB names to maintain compatibility with existing dashboards
    db = client["campeones_mundiales"] 
    col = db["Campeones"]
    
    # Clear the collection before inserting new data to prevent duplicates
    col.delete_many({})
    col.insert_many(records_list)

    print("Data successfully loaded into the Cloud!")
    return db

# ----------------------------------- CLOUD FUNCTION ENTRY POINT ---------------------------------------------
def run_pipeline(request):
    """
    Main entry point for Google Cloud Functions.
    """
    print("Starting pipeline from Google Cloud...")
    try:
        # 1. Extraction
        extracted_tables = extract_champions()

        if len(extracted_tables) > 0:
            # 2. Transformation
            final_df = transform_data(extracted_tables)
            # 3. Loading
            load_data(final_df)
            return "Pipeline executed successfully", 200
        else:
            return "Error: No tables found on Wikipedia.", 500
    except Exception as e:
        print(f'Critical error: {e}')
        return f'Server error occurred: {str(e)}', 500

# ---------------------------------------- LOCAL TEST ---------------------------------------------
if __name__ == "__main__":
    print("--- Local Mode ---")
    run_pipeline(None)


# Useful Commands:
# $ cd C:\\Users\\ASUS\\Documents\\proyectos\\boxing-data-pipeline

# Create virtual environment
# python -m venv venv

# Activate virtual environment
# source venv/Scripts/activate

# Start Docker container
# docker start mi-mongo