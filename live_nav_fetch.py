import requests
import pandas as pd
import json
import os

FILE_SAVE_PATH = "./data/raw"

schemes = {
    "SBI_Bluechip": "119551",
    "ICICI_Bluechip": "120503",
    "Nippon_Large_Cap": "118632",
    "Axis_Bluechip": "119092",
    "Kotak_Bluechip": "120841"
}

def fetch_save_nav(save_path, schemes):
    """function to fetch the data from the url then convert it to dataframe then save it as csv"""
    for nav_name, nav_id in schemes.items():
        url = f"https://api.mfapi.in/mf/{nav_id}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data['data']) > 0:
                df = pd.DataFrame(data['data'])
                csv_file_name = f"{nav_name}_{nav_id}_nav_his.csv"
                csv_file_save_path = os.path.join(save_path, csv_file_name)
                df.to_csv(csv_file_save_path, index=False)
                print(f"Saved NAV data for {nav_name} to {csv_file_save_path}")
            else:
                print(f"No NAV data found for {nav_name} id {nav_id} link {url}.")
        else:
            print(f"Failed to fetch data for {nav_name}. Status code: {response.status_code}")

if __name__ == "__main__":
    fetch_save_nav(FILE_SAVE_PATH, schemes)