"""
Module: data_ingestion.py
Purpose: Ingest and display information about CSV files in a specified directory.
"""

import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO)

path = "data/raw"
def ingestion_data(path):
    """function to fetch the name of all the available csv file in a particular path and
      then print the shape/dtypes/head of the following csv"""
    if not os.path.exists(path):
        logging.info(f"path: {path} does not exist")
        return 
    else:
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
    
    if len(files) == 0:
        logging.info(f"No csv files found in path: {path}")
        return
    
    for file in files:
        try:
            file_path = os.path.join(path, file)
            df = pd.read_csv(file_path)
            logging.info(f"File: {file}")
            logging.info(f"shape: {df.shape}")
            logging.info(f"dtypes: {df.dtypes}")
            logging.info(f"head: {df.head()}")
        except Exception as e:
            logging.info(f"Error reading file {file}: {e}")

if __name__ == "__main__":
    ingestion_data(path)