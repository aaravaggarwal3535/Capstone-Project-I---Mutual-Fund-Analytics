# Bluestock Mutual Fund Analytics: End-to-End Data Engineering & BI Pipeline

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![SQLite](https://img.shields.io/badge/SQLite-Star_Schema-green.svg)
![Power BI](https://img.shields.io/badge/Power_BI-Dashboard-yellow.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-lightgrey.svg)

## 📌 Project Overview
The Indian Mutual Fund industry manages over ₹81 Lakh Crores in AUM, yet retail investors struggle with fragmented raw data and a lack of transparent, institutional-grade risk metrics. 

This Capstone project solves this by building an automated, end-to-end data pipeline. It extracts raw AMFI datasets, cleans and transforms the data, and loads it into a high-performance **SQLite Star Schema**. Finally, it powers an interactive **Power BI Dashboard** to deliver actionable insights, risk-adjusted performance metrics (VaR, CVaR, Sharpe), and dynamic investment recommendations.

---

## 🛠️ Tech Stack & Architecture
*   **Language:** Python (Pandas, NumPy, Logging, Subprocess)
*   **Database:** SQLite3 (Dimensional Modeling / Star Schema)
*   **Business Intelligence:** Power BI (DAX, Interactive Data Visualization)
*   **Analytics:** Jupyter Notebooks (EDA, Tail Risk Modeling)

### ⚙️ Pipeline Architecture
1.  **Data Ingestion (`data_ingestion.py`):** Fetches and validates raw CSV data from the `/data/raw` directory.
2.  **Data Transformation (`data_cleaning.py`):** Normalizes formats, handles missing values, casts correct data types, and standardizes AMC names.
3.  **Database Loading (`db_loader.py` & `load_extra_tables.py`):** Inserts processed data into a Star Schema with a central `dim_fund` table linked to `fact_nav`, `fact_transactions`, and `fact_performance`.
4.  **Analytics Engine (`recommended.py`):** Calculates risk scores and generates investment recommendations based on annualized standard deviation and rolling Sharpe ratios.
5.  **Visualization (`Dashboard`):** Pre-aggregated materialized views feed directly into Power BI for zero-latency rendering.

---

## 🚀 Core Features & Architecture

* **Automated Data Pipeline:** Deployed a scheduled ETL script via GitHub Actions that auto-fetches daily NAV data from `mfapi.in` every weekday at 8:00 PM.
* **Interactive Cloud Dashboard:** Built a dynamic Streamlit web application as a responsive, cloud-hosted alternative to Power BI for seamless data visualization.
* **Monte Carlo Forecasting Engine:** Implemented a stochastic simulation module to project mutual fund NAV growth over a 5-year horizon, complete with probabilistic uncertainty bands.
* **Portfolio Optimization (Modern Portfolio Theory):** Engineered a Markowitz Efficient Frontier optimization module using SciPy to calculate the optimal capital allocation across selected funds to maximize the Sharpe ratio.
* **Automated Newsletter System:** Created a cloud-scheduled email report generator that queries the live subscriber database and broadcasts a stylized HTML weekly performance summary directly to users' inboxes.

## 📂 Repository Structure
```text
C:\internships\
├── dashboard/          # Power BI project file (.pbix)
├── data/               # Raw source CSVs and clean processed outputs
├── db/                 # SQLite database file (bluestock_mf.db)
├── notebooks/          # Exploratory Data Analysis (EDA) and Modeling
├── reports/            # Presentation slides, charts, and Final PDF Report
├── scripts/            # Core ETL pipeline scripts
├── sql/                # SQL schema definitions and query templates
├── run_pipeline.py     # Master orchestrator script
└── requirements.txt    # Python dependencies
```

## Setup & Installation
1. Prerequisites
  Python 3.8 or higher, Power BI Desktop (for viewing the dashboard), Git
2. Local Setup
```bash
$ git clone https://github.com/aaravaggarwal3535/Capstone-Project-I---Mutual-Fund-Analytics.git
$ cd Capstone-Project-I---Mutual-Fund-Analytics
```
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```
3. Installing libraries
```bash
pip install -r requirements.txt
```
4. Run pipeline file
```bash
python run_pipeline.py
```

## To Open The Dashboard
```
Opening the Power BI Dashboard
1. Install Power BI Desktop.
2. Navigate to the dashboard/ folder in this repository.
3. Open bluestock_mf_dashboard.pbix.
4. The dashboard is pre-configured to connect to the local SQLite database. Simply click "Refresh" on the Power BI ribbon to pull the latest pipeline data.
```

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


## Day 6: Advanced Analytics & Risk Metrics

### Task-by-Task Execution Breakdown

**Task 1: Value at Risk (VaR) & Conditional VaR (CVaR) Modeling**
*   **What we did:** Measured extreme downside tail-risk for every fund to understand worst-case scenario daily losses.
*   **How we did it:** Grouped the `fact_nav` table by fund and used `numpy.percentile` to find the 5th percentile of the daily return distribution (95% VaR). We then calculated CVaR by taking the statistical mean of all returns that fell below that VaR threshold.
*   **Output:** `var_cvar_report.csv`

**Task 2: Rolling 90-Day Sharpe Ratio Analysis**
*   **What we did:** Tracked how risk-adjusted returns fluctuate over time, rather than relying on a static multi-year average.
*   **How we did it:** Applied Pandas `.rolling(window=90)` to the daily returns of the top 5 funds to calculate dynamic moving averages and standard deviations. We annualized the results and visualized the cyclicality using Matplotlib.
*   **Output:** `rolling_sharpe_chart.png`

**Task 3: Investor Cohort Analysis**
*   **What we did:** Profiled investor behavior and capital commitment based on the year they made their first transaction.
*   **How we did it:** Used Pandas `groupby` to isolate the minimum transaction date per `investor_id` to establish their cohort year (2024 vs. 2025). We then aggregated the total capital invested, average SIP ticket size, and preferred fund for each cohort.
*   **Output:** `cohort_analysis.csv`

**Task 4: SIP Continuation & At-Risk Flagging**
*   **What we did:** Built an early-warning system to identify investors who are likely pausing or canceling their recurring investments.
*   **How we did it:** Filtered the transactions table for users with 6+ SIPs. We used Pandas `shift(1)` to calculate the exact `dt.days` gap between consecutive payments. Investors averaging a gap greater than 35 days were tagged with an `at_risk_flag`.
*   **Output:** `sip_continuity.csv`

**Task 5: Fund Recommendation Engine**
*   **What we did:** Engineered a simple, terminal-based recommendation script that outputs top funds tailored to a user's risk appetite.
*   **How we did it:** Created a standalone Python script (`recommender.py`) that connects directly to the SQLite database. It dynamically assigns a 'Low', 'Moderate', or 'High' risk grade based on a fund's standard deviation, filters by the user's input, and ranks the top 3 matches using the Sharpe Ratio.
*   **Output:** `recommender.py` (Script)

**Task 6: Sector Concentration Analysis (HHI)**
*   **What we did:** Measured portfolio diversification to flag funds taking heavily concentrated bets on specific sectors.
*   **How we did it:** Calculated the Herfindahl-Hirschman Index (HHI) for each equity fund by squaring the percentage weight of each sector holding (`weight_pct ^ 2`) and summing them. Funds scoring over 1,500–2,000 were flagged and visualized on a horizontal bar chart.
*   **Output:** `sector_hhi.csv` and `sector_hhi_chart.png`

**Task 7: Advanced Analytics Summary**
*   **What we did:** Synthesized the raw mathematical outputs into actionable business insights.
*   **How we did it:** Authored a Jupyter Markdown cell documenting 5 critical findings, including the severe CVaR of small-cap funds, the 97.8% SIP at-risk rate, and the higher average ticket size of newer investor cohorts.
*   **Output:** Appended to `06_advanced_analytics.ipynb`

# By Aarav Aggarwal
## LinkedIn: https://www.linkedin.com/in/aarav-aggarwal35/
## Portfolio: aaravaggarwal.vercel.app
## Email: aaravaggarwal3535@gmail.com