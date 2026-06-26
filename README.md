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

## Day 2: Data Cleaning + SQL Database Design

### Step 1: Data Cleaning (All 10 Datasets)
```text
Script: data_cleaning.py

Execution: 
- Performed a general cleaning pass across all datasets to drop duplicates and strip hidden whitespace.
- Applied specific, strict business logic to the core datasets:
  - nav_history: Parsed dates to datetime, sorted by amfi_code and date, forward-filled missing NAVs, and validated NAV > 0.
  - investor_transactions: Standardized transaction types (Sip/Lumpsum/Redemption), validated amounts > 0, and handled missing KYC statuses.
  - scheme_performance: Ensured returns were numeric, validated expense ratio ranges (0.1% - 2.5%), and created a boolean flag for negative Sharpe ratios.
```

### Step 2: Design SQLite Schema
```
File: sql/schema.sql

Execution: Designed a relational database structure matching the exact cleaned CSV columns. Defined Primary Keys, Foreign Keys (linked via amfi_code), and strict data types for 4 core tables:
- dim_fund (Dimension table for fund details)
- fact_nav (Fact table for historical NAVs)
- fact_transactions (Fact table for investor activity)
- fact_performance (Fact table for scheme metrics)
```

### Step 3: Load Cleaned Data into Database
```
Script: db_loader.py

Execution: Utilized SQLAlchemy to connect to an SQLite database (bluestock_mf.db). Executed the schema.sql file first to enforce strict table structures, then ingested the processed CSVs using Pandas `.to_sql()` with `if_exists='append'` to maintain data integrity.
```

### Step 4: Write Analytical SQL Queries
```
File: sql/queries.sql

Execution: Wrote 10 industry-standard analytical queries, including:
- Top 5 funds by total transaction amount (proxy for AUM).
- Average NAV per month for specific funds.
- Total SIP inflows year-over-year.
- Transaction volume grouped by state demographics.
- Identifying funds with expense ratios < 1% and flagging those with negative Sharpe ratios.
```

### Step 5: Data Dictionary Creation
```
File: reports/data_dictionary.md

Execution: Documented all columns, data types, and data sources for the newly created SQLite database to ensure clear technical hand-offs.
```

### Step 6: Version Control & Finalization
```
Remote repository updated with message: 'Day 2: Cleaned data + SQLite DB loaded'.
```

## Day 3: Exploratory Data Analysis (EDA)

### Step 1: Market Trends & AUM Analysis
```text
Notebook: notebooks/03_eda_analysis.ipynb

Execution: 
- Plotted interactive daily NAV trend lines (2022–2026) using Plotly, highlighting the 2023 rally and 2024 corrections.
- Generated a grouped bar chart in Seaborn showcasing AUM growth by fund house, specifically highlighting SBI's dominance at the ~Rs. 12.5L Crore mark.
```

### Step 2: Inflow & Demographic Behavior
```
Execution:
- Visualized monthly SIP inflows using Plotly, marking the historic Rs. 31,002 Cr milestone.
- Created a Seaborn heatmap to track net inflows across various mutual fund categories over time.
- Analyzed investor demographics by building age group distribution pie charts and SIP amount box plots (log scale) to identify outlier spending behaviors.
- Mapped geographic distributions comparing T30 (Top 30) vs B30 cities to measure retail penetration.
```

### Step 3: Industry Growth & Portfolio Metrics
```
Execution:
- Tracked industry folio count growth from 13.26 Cr to 26.12 Cr using Plotly line charts.
- Computed and visualized a pairwise correlation matrix of daily NAV returns for the Top 10 AUM funds to assess diversification potential.
- Built a donut chart detailing the top sector allocations (Banking & IT) across equity portfolios.
```

### Step 4: Insights & Documentation
```
Execution: Summarized 10 key data-driven findings into the final Jupyter Markdown cell, detailing market resilience, retail confidence, and portfolio concentration. All 9 charts were successfully exported as high-resolution PNGs to the `reports/charts/` directory.
```

## Day 4: Fund Performance Analytics

### Step 1: Core Performance Metrics Calculation
```text
Notebook: notebooks/04_performance_analytics.ipynb

Execution: 
- Computed daily arithmetic returns for all 40 schemes and transformed them into annualized figures.
- Calculated exact 1-year, 3-year, and 5-year Compound Annual Growth Rates (CAGR) dynamically using date offsets from the latest available NAV.
```

### Step 2: Risk-Adjusted Modeling
```
Execution:
- Computed the Sharpe Ratio assuming a risk-free rate of 6.5% (RBI proxy).
- Calculated the Sortino Ratio by isolating downside standard deviation using only negative return days.
- Derived Alpha and Beta by executing an Ordinary Least Squares (OLS) linear regression of fund daily returns against the Nifty 100 benchmark.
- Calculated Maximum Drawdown over the dataset lifespan, flagging the exact dates of peak-to-trough drops.
```

### Step 3: Composite Fund Scorecard Design
```
Execution: Designed a weighted scoring model (0-100 scale) to programmatically identify the best funds. 
- Algorithm: 30% (3Y CAGR) + 25% (Sharpe) + 20% (Alpha) + 15% (Inverse Expense Ratio) + 10% (Max Drawdown).
- Output: Generated `fund_scorecard.csv` to serve as the backend logic for the final recommendation engine.
```

### Step 4: Benchmark Comparison
```
Execution: Mapped the cumulative returns of the Top 5 scored funds against the Nifty 50 and Nifty 100 indices over a 3-year period. Extracted and documented the annualized Tracking Error for each top fund against the Nifty 100 to assess index deviation.
```

## Day 5: Dashboard Development (Power BI)

### Overview
Successfully built a highly interactive, 4-page Power BI dashboard connected directly to the processed data models. Established a robust Star Schema linking the `dim_fund` master dimension table to multiple fact and aggregate tables to enable cross-filtering and deep-dive analytics.

### Dashboard Architecture
1. **Industry Overview:** Executive KPI tracking for Total AUM (~Rs. 81L Cr), active folios (26.12 Cr), and SIP Inflows, supported by a Top 10 AMC concentration bar chart.
2. **Fund Performance:** Engineered an interactive Risk (Standard Deviation) vs. Return (3-Year CAGR) scatter plot, integrated with a dynamically sortable quantitative scorecard matrix. 
3. **Investor Analytics:** Visualized geographic SIP distribution across states and analyzed demographic payment behaviors, highlighting average SIP values across distinct age groups.
4. **SIP & Market Trends:** Designed dual-axis trendlines and a conditional-formatted matrix heatmap to track categorical capital rotation and retail momentum against market indices.

### Deliverables Generated
- `bluestock_mf_dashboard.pbix` (Interactive Power BI Source File)
- `Dashboard.pdf` (Static Executive Export)
- High-resolution dashboard page screenshots (`reports/` folder)
