# Data Dictionary - Bluestock MF Database

## `dim_fund` (Source: 01_fund_master.csv)
* **amfi_code** (INTEGER): Primary Key. Unique identifier for the mutual fund.
* **fund_house / scheme_name** (TEXT): AMC name and official scheme name.
* **category / sub_category** (TEXT): Broad classification and specific focus.
* **plan** (TEXT): Direct or Regular plan type.
* **launch_date** (DATE): Date the fund was launched.
* **benchmark** (TEXT): The benchmark index for the fund.
* **expense_ratio_pct / exit_load_pct** (REAL): Fee percentages.
* **min_sip_amount / min_lumpsum_amount** (INTEGER): Minimum investment requirements.
* **fund_manager** (TEXT): Name of the lead fund manager.
* **risk_category** (TEXT): Risk level (e.g., Very High).
* **sebi_category_code** (TEXT): Regulatory classification code.

## `fact_nav` (Source: 02_nav_history.csv)
* **amfi_code** (INTEGER): Foreign Key linked to dim_fund.
* **date** (DATE): Date of the NAV valuation (YYYY-MM-DD).
* **nav** (REAL): Net Asset Value on the given date.

## `fact_transactions` (Source: 08_investor_transactions.csv)
* **investor_id** (TEXT): Unique ID for the investor.
* **transaction_date** (DATE): Date of execution.
* **amfi_code** (INTEGER): Foreign Key linked to dim_fund.
* **transaction_type** (TEXT): Standardized type (Sip, Lumpsum, Redemption).
* **amount_inr** (INTEGER): Monetary value of the transaction in INR.
* **state / city / city_tier** (TEXT): Location demographics of the investor.
* **age_group / gender / annual_income_lakh** (TEXT/REAL): Investor demographics.
* **payment_mode** (TEXT): Method of payment.
* **kyc_status** (TEXT): Investor verification status.

## `fact_performance` (Source: 07_scheme_performance.csv)
* **amfi_code** (INTEGER): Primary Key linked to dim_fund.
* **scheme_name / fund_house / category / plan** (TEXT): Denormalized fund details.
* **return_1yr_pct / return_3yr_pct / return_5yr_pct** (REAL): Percentage returns.
* **benchmark_3yr_pct** (REAL): Benchmark return for comparison.
* **alpha / beta / sharpe_ratio / sortino_ratio** (REAL): Risk and volatility metrics.
* **std_dev_ann_pct / max_drawdown_pct** (REAL): Risk metrics.
* **aum_crore** (INTEGER): Total Assets Under Management in Crores.
* **expense_ratio_pct** (REAL): Fund management fee percentage.
* **morningstar_rating** (INTEGER): External rating score.
* **risk_grade** (TEXT): Text representation of risk.
* **negative_sharpe_flag** (BOOLEAN): True if sharpe_ratio < 0.