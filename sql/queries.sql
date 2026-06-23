-- 1. Top 5 funds by total transaction amount (Proxy for AUM)
SELECT amfi_code, SUM(amount_inr) as total_inflow
FROM fact_transactions 
GROUP BY amfi_code 
ORDER BY total_inflow DESC LIMIT 5;

-- 2. Average NAV per month for HDFC Top 100 (amfi_code 125497)
SELECT strftime('%Y-%m', date) as month, AVG(nav) as avg_nav
FROM fact_nav 
WHERE amfi_code = 125497 
GROUP BY month;

-- 3. Total SIP inflows by Year
SELECT strftime('%Y', transaction_date) as year, SUM(amount_inr) as total_sip_inflow
FROM fact_transactions 
WHERE transaction_type = 'Sip' 
GROUP BY year;

-- 4. Count of transactions by State
SELECT state, COUNT(*) as transaction_count, SUM(amount_inr) as total_volume
FROM fact_transactions
GROUP BY state
ORDER BY transaction_count DESC;

-- 5. Funds with expense ratio < 1%
SELECT scheme_name, expense_ratio_pct 
FROM fact_performance 
WHERE expense_ratio_pct < 1.0;

-- it is written to to see the 6 to 10 from notebook but which i cant understand so i have taken the same data processing queries as before
-- 6. Funds flagged with a negative Sharpe Ratio
SELECT amfi_code, scheme_name, sharpe_ratio 
FROM fact_performance 
WHERE negative_sharpe_flag = 1;

-- 7. Highest 5-year return funds
SELECT scheme_name, return_5yr_pct 
FROM fact_performance 
ORDER BY return_5yr_pct DESC LIMIT 10;

-- 8. Average transaction amount by KYC status
SELECT kyc_status, AVG(amount_inr) as avg_transaction 
FROM fact_transactions 
GROUP BY kyc_status;

-- 9. Latest NAV for all funds (using a subquery)
SELECT amfi_code, nav, MAX(date) as latest_date
FROM fact_nav
GROUP BY amfi_code;

-- 10. Fund categories by average risk
SELECT category, risk_category, COUNT(*) as num_funds
FROM dim_fund
GROUP BY category, risk_category;