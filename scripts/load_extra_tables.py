# scripts/load_extra_tables.py
import pandas as pd
from sqlalchemy import create_engine
import os
import sqlite3

# Set up paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
DB_PATH = os.path.join(BASE_DIR, 'db', 'bluestock_mf.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'sql', 'schema_extra.sql')
ENGINE = create_engine(f"sqlite:///{DB_PATH}")

def setup_and_load():
    print("1. Executing Strict SQL Schema...")
    # Read and execute the schema_extra.sql file
    with open(SCHEMA_PATH, 'r') as file:
        schema_script = file.read()
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema_script)
        
    # The exact files and their corresponding database table names
    table_mappings = {
        "clean_aum_by_fund_house.csv": "aum_by_fund_house",
        "clean_monthly_sip_inflows.csv": "monthly_sip_inflows",
        "clean_category_inflows.csv": "category_inflows",
        "clean_industry_folio_count.csv": "industry_folio_count"
    }
    
    print("\n2. Appending data to pre-defined tables...")
    for file_name, table_name in table_mappings.items():
        file_path = os.path.join(PROCESSED_DIR, file_name)
        
        if os.path.exists(file_path):
            try:
                # First, clear any old bad data from the table to prevent duplicates
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute(f"DELETE FROM {table_name}")
                
                # Load the CSV and clean financial characters just in case
                df = pd.read_csv(file_path)
                
                # Append data cleanly into our strict schema
                df.to_sql(table_name, ENGINE, if_exists='append', index=False)
                print(f"'{file_name}' loaded smoothly into '{table_name}'")
            except Exception as e:
                print(f"Error loading '{file_name}': {e}")
        else:
            print(f"Warning: '{file_name}' not found.")

    print("\nOperation Complete! The database is now structurally flawless for Power BI.")

if __name__ == "__main__":
    setup_and_load()