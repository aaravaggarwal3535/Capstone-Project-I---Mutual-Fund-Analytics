# Mutual Fund Analytics Capstone

## Day 1: Project Setup + Data Ingestion (ETL)

### Step 1: Project Folder Structure Created
Set up the foundational directory structure for the analytics pipeline to ensure organized data management and scalable code.

```
C:\internship\
├── .venv/                  # Python Virtual Environment (Git Ignored)
├── data/
│   ├── raw/                # Unprocessed datasets (16 CSVs total)
│   └── processed/          # Cleaned and transformed datasets
├── notebooks/              # Jupyter notebooks for EDA and testing
├── sql/                    # SQL scripts for database operations
├── dashboard/              # Code for the final interactive dashboard
├── reports/                # Generated text and visual reports
├── .gitignore              # Hides .venv, pycache, and checkpoints
├── data_ingestion.py       # Python script for initial CSV loading
├── live_nav_fetch.py       # Python script for API data fetching
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

### Step 2: Install Dependencies
```
# Install dependencies
pip install pandas numpy matplotlib seaborn plotly sqlalchemy requests jupyter

# Save them to requirements.txt
pip freeze > requirements.txt
```

### Step 3: Ingest Local CSV Datasets
```
Script: data_ingestion.py

Execution: Iterates through data/raw/, reads each CSV using Pandas, and outputs the .shape, .dtypes, and .head() to the console for quick validation.
```

### Step 4 & 5: Fetch Live NAV Data via API
```
Script: live_nav_fetch.py

Execution: Sent GET requests to the API, parsed the JSON response, and converted the historical NAV data into raw CSV files.

Target Schemes:

SBI Bluechip (119551)

ICICI Bluechip (120503)

Nippon Large Cap (118632)

Axis Bluechip (119092)

Kotak Bluechip (120841)
```

### Step 6: Understand Fund Master (EDA)
```
Notebook: notebooks/Day1_EDA.ipynb

Execution: Loaded 01_fund_master.csv and successfully printed the unique values for:

Fund Houses

Categories

Sub-categories

Risk Grades
```

### Step 7: Validate AMFI Codes (Data Quality Report)
```
Notebook: notebooks/Day1_EDA.ipynb

Execution: Utilized a Pandas Left Merge (pd.merge(..., how='left')) to cross-reference fund_master with nav_history.
```

### Step 8: Version Control & Finalization
```
Remote repository updated with message: 'Day 1: Data ingestion complete'.
```