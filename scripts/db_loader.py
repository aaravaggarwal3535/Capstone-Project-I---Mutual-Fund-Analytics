"""
Module: db_loader.py
Purpose: Load processed data into a SQLite database.
"""

import pandas as pd
from sqlalchemy import create_engine
import os
import logging

logging.basicConfig(level=logging.INFO)

PROCESSED_DIR = "data/processed"
DB_PATH = "sqlite:///db/bluestock_mf.db"
SCHEMA_PATH = "sql/schema.sql"

def load_database(processed_dir, db_path, schema_path):
    """Load processed CSV files into a SQLite database."""

    engine = create_engine(db_path, echo=False)
    
    # 1. Initialize schema
    logging.info("Executing schema.sql to build/reset table structures")
    with engine.connect() as conn:
        raw_conn = conn.connection
        with open(schema_path, "r") as f:
            raw_conn.executescript(f.read())
    logging.info("Schema applied successfully")

    # 2. Define your table mappings (Filename : Table Name)
    table_map = {
        "clean_fund.csv": "dim_fund",
        "clean_nav.csv": "fact_nav",
        "clean_transactions.csv": "fact_transactions",
        "clean_performance.csv": "fact_performance"
    }

    # 3. Load files using 'replace' to ensure fresh data
    for filename, table_name in table_map.items():
        file_path = os.path.join(processed_dir, filename)
        if os.path.exists(file_path):
            logging.info(f"Loading {filename} into {table_name}")
            df = pd.read_csv(file_path)
            # 'replace' drops the old table and writes the fresh CSV, 
            # ensuring Primary Key constraints are not violated.
            df.to_sql(table_name, engine, if_exists='replace', index=False)
        else:
            logging.warning(f"File not found: {file_path}")

if __name__ == "__main__":
    load_database(PROCESSED_DIR, DB_PATH, SCHEMA_PATH)