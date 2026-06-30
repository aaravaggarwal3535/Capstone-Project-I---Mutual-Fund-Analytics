"""
Module: db_loader.py
Purpose: Load processed data into a SQLite database.
"""

import pandas as pd
from sqlalchemy import create_engine
import os
import logging

logging.basicConfig(level=logging.INFO)

PROCESSED_DIR = "../data/processed"
DB_PATH = "sqlite:///../db/bluestock_mf.db"
SCHEMA_PATH = "../sql/schema.sql"

def load_database(processed_dir, db_path, schema_path):
    """Load processed CSV files into a SQLite database.
    Args:
        processed_dir (str): Path to the directory containing processed CSV files.
        db_path (str): Path to the SQLite database.
        schema_path (str): Path to the SQL schema file.
    """

    engine = create_engine(db_path, echo=False)
    logging.info("Executing schema.sql to build tables")
    with engine.connect() as conn:
        raw_conn = conn.connection
        with open(schema_path, "r") as f:
            raw_conn.executescript(f.read())
    logging.info("Tables created successfully")
    # Load dim_fund
    logging.info("Loading dim_fund")
    df_fund = pd.read_csv(os.path.join(processed_dir, "clean_fund.csv"))
    df_fund.to_sql('dim_fund', engine, if_exists='append', index=False)

    # Load fact_nav
    logging.info("Loading fact_nav")
    df_nav = pd.read_csv(os.path.join(processed_dir, "clean_nav.csv"))
    df_nav.to_sql('fact_nav', engine, if_exists='append', index=False)

    # Load fact_transactions
    logging.info("Loading fact_transactions")
    df_trans = pd.read_csv(os.path.join(processed_dir, "clean_transactions.csv"))
    df_trans.to_sql('fact_transactions', engine, if_exists='append', index=False)

    # Load fact_performance
    logging.info("Loading fact_performance")
    df_perf = pd.read_csv(os.path.join(processed_dir, "clean_performance.csv"))
    df_perf.to_sql('fact_performance', engine, if_exists='append', index=False)
    
if __name__ == "__main__":
    load_database(PROCESSED_DIR, DB_PATH, SCHEMA_PATH)