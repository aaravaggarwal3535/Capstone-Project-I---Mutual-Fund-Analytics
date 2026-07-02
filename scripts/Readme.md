# Scripts Directory
Core Python logic for the ETL (Extract, Transform, Load) pipeline.

- `data_ingestion.py`: Pulls and validates raw source data.
- `data_cleaning.py`: Normalizes data formats and handles missing values.
- `db_loader.py`: Handles the insertion of processed data into the SQLite database.
- `load_extra_tables.py`: Manages auxiliary reference tables.
- `recommended.py`: Executes the investment recommendation and risk-scoring logic.
- `live_nav_fetch.py`: Module for fetching latest NAV updates.