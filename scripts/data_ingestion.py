import pandas as pd
import os

path = "../data/raw"
def ingestion_data(path):
    """function to fetch the name of all the available csv file in a particular path and
      then print the shape/dtypes/head of the following csv"""
    if not os.path.exists(path):
        print(f"path: {path} does not exist")
        return 
    else:
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
    
    if len(files) == 0:
        print(f"No csv files found in path: {path}")
        return
    
    for file in files:
        try:
            file_path = os.path.join(path, file)
            df = pd.read_csv(file_path)
            print(f"File: {file}")
            print(f"shape: {df.shape}")
            print(f"dtypes: {df.dtypes}")
            print(f"head: {df.head()}")
        except Exception as e:
            print(f"Error reading file {file}: {e}")

if __name__ == "__main__":
    ingestion_data(path)