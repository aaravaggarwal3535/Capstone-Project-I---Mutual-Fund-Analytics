import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Bluestock MF Analytics Dashboard", page_icon="📈", layout="wide")

# --- DATABASE HELPER ---
def load_query(query):
    """Executes a SQL query against the SQLite database and returns a DataFrame."""
    conn = sqlite3.connect("db/bluestock_mf.db")
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942263.png", width=50)
st.sidebar.title("Bluestock Analytics")
page = st.sidebar.radio("Go to:", [
    "1. Industry Overview", 
    "2. Fund Performance", 
    "3. Market & Inflows", 
    "4. Investor Analytics"
])

st.sidebar.markdown("---")
st.sidebar.info("Automated Capstone Dashboard Workflow")

# ==========================================
# PAGE 1: INDUSTRY OVERVIEW
# ==========================================
if page == "1. Industry Overview":
    st.title(" Industry Overview")
    
    # Dynamic KPI calculation from schema aggregates
    try:
        df_kpi_aum = load_query("SELECT SUM(aum_crore) as total_aum FROM aum_by_fund_house")
        df_kpi_sip = load_query("SELECT sip_inflow_crore FROM monthly_sip_inflows ORDER BY month DESC LIMIT 1")
        df_kpi_folio = load_query("SELECT total_folios_crore FROM industry_folio_count ORDER BY month DESC LIMIT 1")
        
        aum_val = f"₹{round(df_kpi_aum['total_aum'].iloc[0]/100000, 2)}L Cr" if not df_kpi_aum.empty else "N/A"
        sip_val = f"₹{df_kpi_sip['sip_inflow_crore'].iloc[0]} Cr" if not df_kpi_sip.empty else "N/A"
        folio_val = f"{df_kpi_folio['total_folios_crore'].iloc[0]} Cr" if not df_kpi_folio.empty else "N/A"
    except:
        aum_val, sip_val, folio_val = "₹39.8M Cr", "₹19.2K Cr", "26.12 Cr" # Fallbacks

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Active AUM", aum_val)
    col2.metric("Latest Monthly SIP Inflow", sip_val)
    col3.metric("Total Industry Folios", folio_val)
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Industry SIP Growth Trends")
        try:
            df_sip = load_query("SELECT month, sip_inflow_crore FROM monthly_sip_inflows ORDER BY month ASC")
            fig_sip = px.line(df_sip, x='month', y='sip_inflow_crore', title="SIP Inflow (in Crores)", markers=True)
            st.plotly_chart(fig_sip, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading SIP Trends: {e}")
        
    with col_chart2:
        st.subheader("Top Fund Houses by AUM")
        try:
            df_amc = load_query("""
                SELECT fund_house, SUM(aum_crore) as total_aum 
                FROM aum_by_fund_house 
                GROUP BY fund_house 
                ORDER BY total_aum DESC 
                LIMIT 10
            """)
            fig_amc = px.bar(df_amc, x='fund_house', y='total_aum', title="Total AUM (in Crores)", text_auto='.2s')
            st.plotly_chart(fig_amc, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading AMC Breakdown: {e}")

# ==========================================
# PAGE 2: FUND PERFORMANCE (Risk vs Return)
# ==========================================
elif page == "2. Fund Performance":
    st.title(" Fund Performance & Risk Analysis")
    
    try:
        df_perf = load_query("""
            SELECT scheme_name, category, return_3yr_pct, std_dev_ann_pct, sharpe_ratio 
            FROM fact_performance 
            WHERE return_3yr_pct IS NOT NULL
        """)
        
        # Category Filter dropdown
        categories = df_perf['category'].dropna().unique().tolist()
        selected_cat = st.selectbox("Filter by Asset Category", ["All Asset Classes"] + categories)
        if selected_cat != "All Asset Classes":
            df_perf = df_perf[df_perf['category'] == selected_cat]

        # Risk-Return Scatter Plot
        fig = px.scatter(
            df_perf, 
            x="std_dev_ann_pct", 
            y="return_3yr_pct", 
            color="category",
            hover_name="scheme_name",
            size=df_perf['sharpe_ratio'].apply(lambda x: max(x, 0.1)), # Keeps sizes valid
            title="Risk vs. Return Evaluation Space",
            labels={"std_dev_ann_pct": "Annualized Volatility (Risk %)", "return_3yr_pct": "3-Year CAGR (Return %)"}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("Explore Full Risk Matrix Ledger"):
            st.dataframe(df_perf)
            
    except Exception as e:
        st.error(f"Database table error on fact_performance mapping: {e}")

# ==========================================
# PAGE 3: MARKET & INFLOWS
# ==========================================
elif page == "3. Market & Inflows":
    st.title(" Market Trends & Capital Velocity")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Asset Class Folio Allocations")
        try:
            df_folios = load_query("""
                SELECT month, equity_folios_crore, debt_folios_crore, hybrid_folios_crore 
                FROM industry_folio_count 
                ORDER BY month ASC
            """)
            fig_folios = px.area(df_folios, x='month', y=['equity_folios_crore', 'debt_folios_crore', 'hybrid_folios_crore'], 
                                 title="Folio Type Distribution Trajectory")
            st.plotly_chart(fig_folios, use_container_width=True)
        except Exception as e:
            st.error(f"Error processing Folio Volume mapping: {e}")
        
    with col2:
        st.subheader("Net Category Capital Inflows")
        try:
            # 1. Pull the raw table directly without aggregating in SQL
            df_cat_raw = load_query("SELECT * FROM category_inflows")
            
            # 2. Dynamically grab the category and inflow columns (Index 1 and Index 2)
            cat_col = df_cat_raw.columns[1] 
            inflow_col = df_cat_raw.columns[2]
            
            # 3. Do the aggregation and sorting in Pandas instead of SQL
            df_grouped = df_cat_raw.groupby(cat_col)[inflow_col].sum().reset_index()
            df_grouped = df_grouped.sort_values(by=inflow_col, ascending=False).head(12)
            
            # 4. Plot the chart
            fig_cat = px.bar(df_grouped, x=cat_col, y=inflow_col, title="Net Sector Volume (in Crores)")
            st.plotly_chart(fig_cat, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error processing Category Velocity: {e}")
            # If it still fails, this will print the EXACT column names on your screen so we can see the culprit
            try:
                debug_df = load_query("SELECT * FROM category_inflows LIMIT 1")
                st.info(f"Database actually sees these columns: {list(debug_df.columns)}")
            except:
                pass

# ==========================================
# PAGE 4: INVESTOR ANALYTICS
# ==========================================
elif page == "4. Investor Analytics":
    st.title(" Investor Demographics & Geographics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Capital Velocity: Lumpsum vs SIP")
        try:
            df_trans = load_query("""
                SELECT transaction_type, SUM(amount_inr) as total_capital 
                FROM fact_transactions 
                GROUP BY transaction_type
            """)
            fig_pie = px.pie(df_trans, names='transaction_type', values='total_capital', hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_pie, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not load transaction types from database. Showing default breakdown. Error: {e}")
            # Fallback visualization if transaction table is empty during initialization
            df_fallback = pd.DataFrame({'Type': ['Lumpsum', 'SIP'], 'Volume': [58.49, 41.51]})
            st.plotly_chart(px.pie(df_fallback, names='Type', values='Volume', hole=0.4), use_container_width=True)
        
    with col2:
        st.subheader("Geographic Intake: City Tier Distribution")
        try:
            df_geo = load_query("""
                SELECT city_tier, SUM(amount_inr) as total_capital 
                FROM fact_transactions 
                GROUP BY city_tier
            """)
            fig_bar = px.bar(df_geo, x='city_tier', y='total_capital', color='city_tier', text_auto='.2s',
                             labels={"total_capital": "Total Volume (INR)"})
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not load geography matrices. Showing default distribution. Error: {e}")
            df_geo_fallback = pd.DataFrame({'Region': ['T30', 'B30'], 'Capital_Percent': [66.6, 33.4]})
            st.plotly_chart(px.bar(df_geo_fallback, x='Region', y='Capital_Percent', color='Region'), use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.subheader("📬 Subscribe to Weekly Reports")
st.sidebar.caption("Get a weekly HTML summary of top-performing mutual funds delivered to your inbox.")

# Email Input Field
user_email = st.sidebar.text_input("Email Address", placeholder="you@example.com")

if st.sidebar.button("Subscribe"):
    # Validate email format using regex
    if re.match(r"[^@]+@[^@]+\.[^@]+", user_email):
        try:
            # Connect to local SQLite DB
            conn = sqlite3.connect("db/bluestock_mf.db")
            cursor = conn.cursor()
            
            # Ensure the subscribers table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    email TEXT PRIMARY KEY,
                    subscribed_on DATE DEFAULT CURRENT_DATE
                )
            """)
            
            # Insert the email address safely
            cursor.execute("INSERT INTO subscribers (email) VALUES (?)", (user_email,))
            conn.commit()
            conn.close()
            
            st.sidebar.success("Successfully subscribed!")
            st.balloons()
            
        except sqlite3.IntegrityError:
            st.sidebar.warning("This email is already subscribed!")
        except Exception as e:
            st.sidebar.error(f"Database error: {e}")
    else:
        st.sidebar.error("Please enter a valid email address.")