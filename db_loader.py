# db_loader.py
import pandas as pd
from sqlalchemy import create_engine
import os

PROCESSED_DIR = "./data/processed"
DB_PATH = "sqlite:///./sql/bluestock_mf.db"
SCHEMA_PATH = "./sql/schema.sql"

def load_database(processed_dir, db_path, schema_path):
    engine = create_engine(db_path, echo=False)
    print("Executing schema.sql to build tables")
    with engine.connect() as conn:
        raw_conn = conn.connection
        with open(schema_path, "r") as f:
            raw_conn.executescript(f.read())
    print("Tables created successfully")
    # Load dim_fund
    print("Loading dim_fund")
    df_fund = pd.read_csv(os.path.join(processed_dir, "clean_fund.csv"))
    df_fund.to_sql('dim_fund', engine, if_exists='append', index=False)

    # Load fact_nav
    print("Loading fact_nav")
    df_nav = pd.read_csv(os.path.join(processed_dir, "clean_nav.csv"))
    df_nav.to_sql('fact_nav', engine, if_exists='append', index=False)

    # Load fact_transactions
    print("Loading fact_transactions")
    df_trans = pd.read_csv(os.path.join(processed_dir, "clean_transactions.csv"))
    df_trans.to_sql('fact_transactions', engine, if_exists='append', index=False)

    # Load fact_performance
    print("Loading fact_performance")
    df_perf = pd.read_csv(os.path.join(processed_dir, "clean_performance.csv"))
    df_perf.to_sql('fact_performance', engine, if_exists='append', index=False)
    
if __name__ == "__main__":
    load_database(PROCESSED_DIR, DB_PATH, SCHEMA_PATH)