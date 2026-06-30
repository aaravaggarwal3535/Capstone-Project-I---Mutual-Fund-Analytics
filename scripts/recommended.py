"""
Module: recommended.py
Purpose: Recommend mutual funds based on the user's risk appetite.
"""

import pandas as pd
import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)

def recommend_funds(risk_appetite):
    """Recommend top 3 mutual funds based on the user's risk appetite."""
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(BASE_DIR, 'db', 'bluestock_mf.db')
    
    if not os.path.exists(db_path):
        logging.info("Database not found.")
        return "Database not found."

    conn = sqlite3.connect(db_path)
    
    query = """
    SELECT f.scheme_name, f.category, p.sharpe_ratio, p.std_dev_ann_pct 
    FROM dim_fund f
    JOIN fact_performance p ON f.amfi_code = p.amfi_code
    WHERE p.sharpe_ratio IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    conn.close()

    def assign_risk(std):
        if std < 10.0: return 'Low'
        elif 10.0 <= std < 18.0: return 'Moderate'
        else: return 'High'
            
    df['risk_grade'] = df['std_dev_ann_pct'].apply(assign_risk)
    filtered = df[df['risk_grade'].str.lower() == risk_appetite.lower()]
    
    if filtered.empty:
        logging.info(f"No funds found matching risk profile: {risk_appetite}")
        return f"No funds found matching risk profile: {risk_appetite}"
        
    top_3 = filtered.sort_values('sharpe_ratio', ascending=False).head(3)
    
    logging.info(f"\n--- Top 3 Fund Recommendations for {risk_appetite.upper()} Risk ---")
    logging.info(top_3[['scheme_name', 'category', 'sharpe_ratio', 'std_dev_ann_pct']].to_string(index=False))
    logging.info("-" * 60)
    
    return top_3

if __name__ == "__main__":
    recommend_funds('Low')
    recommend_funds('Moderate')
    recommend_funds('High')