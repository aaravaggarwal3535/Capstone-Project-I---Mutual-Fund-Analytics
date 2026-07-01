"""
Bluestock Weekly Market Intelligence Briefing
------------------------------------------------
Pulls a multi-angle snapshot of the mutual fund universe (AUM trend, SIP
flows, folio growth, top performers, risk-adjusted leaders, category
rotation, and risk alerts) from the local warehouse and emails a
publication-grade HTML briefing to the Supabase subscriber list.
"""

import os
import sqlite3
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pandas as pd

DB_PATH = "db/bluestock_mf.db"
DASHBOARD_URL = "https://mutual-fund-analytics.streamlit.app/"


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_crore(value):
    """Render a crore figure, auto-scaling to Lakh Cr for big numbers."""
    if value is None or pd.isna(value):
        return "N/A"
    if value >= 100000:
        return f"₹{value / 100000:.2f} Lakh Cr"
    return f"₹{value:,.0f} Cr"


def fmt_pct(value, decimals=2):
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}%"


def fmt_num(value, decimals=2):
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:,.{decimals}f}"


def fmt_stars(rating):
    try:
        r = int(rating)
        r = max(0, min(5, r))
    except (TypeError, ValueError):
        return '<span style="color:#cbd5e1;">Unrated</span>'
    return f'<span style="color:#f59e0b; letter-spacing:1px;">{"★" * r}{"☆" * (5 - r)}</span>'


def change_badge(pct, decimals=1):
    if pct is None or pd.isna(pct):
        return '<span style="color:#94a3b8; font-size:12px;">—</span>'
    color = "#16a34a" if pct >= 0 else "#dc2626"
    arrow = "▲" if pct >= 0 else "▼"
    return f'<span style="color:{color}; font-weight:600; font-size:12px;">{arrow} {abs(pct):.{decimals}f}%</span>'


def fmt_month(value):
    if value is None or pd.isna(value):
        return "N/A"
    try:
        return pd.to_datetime(value).strftime("%b %Y")
    except (ValueError, TypeError):
        return str(value)


# ---------------------------------------------------------------------------
# Data access
# ---------------------------------------------------------------------------

def safe_query(conn, query, label):
    """Run a query and swallow errors so one bad table never kills the report."""
    try:
        return pd.read_sql(query, conn)
    except Exception as e:
        print(f"[warn] '{label}' query failed: {e}")
        return pd.DataFrame()


def fetch_market_pulse(conn):
    pulse = {}

    aum_df = safe_query(
        conn,
        "SELECT date, SUM(aum_crore) AS total_aum FROM aum_by_fund_house "
        "GROUP BY date ORDER BY date DESC LIMIT 2",
        "AUM trend",
    )
    if len(aum_df) >= 1:
        pulse["aum_latest"] = aum_df.iloc[0]["total_aum"]
        pulse["aum_date"] = aum_df.iloc[0]["date"]
        if len(aum_df) >= 2 and aum_df.iloc[1]["total_aum"]:
            prev = aum_df.iloc[1]["total_aum"]
            pulse["aum_change_pct"] = (pulse["aum_latest"] - prev) / prev * 100

    sip_df = safe_query(
        conn,
        "SELECT month, sip_inflow_crore, yoy_growth_pct FROM monthly_sip_inflows "
        "ORDER BY month DESC LIMIT 1",
        "SIP inflows",
    )
    if len(sip_df):
        pulse["sip_inflow"] = sip_df.iloc[0]["sip_inflow_crore"]
        pulse["sip_yoy"] = sip_df.iloc[0]["yoy_growth_pct"]
        pulse["sip_month"] = sip_df.iloc[0]["month"]

    folio_df = safe_query(
        conn,
        "SELECT month, total_folios_crore FROM industry_folio_count "
        "ORDER BY month DESC LIMIT 2",
        "folio count",
    )
    if len(folio_df) >= 1:
        pulse["folios"] = folio_df.iloc[0]["total_folios_crore"]
        pulse["folio_month"] = folio_df.iloc[0]["month"]
        if len(folio_df) >= 2 and folio_df.iloc[1]["total_folios_crore"]:
            prev = folio_df.iloc[1]["total_folios_crore"]
            pulse["folio_change_pct"] = (pulse["folios"] - prev) / prev * 100

    return pulse


def fetch_top_performers(conn, n=5):
    return safe_query(
        conn,
        "SELECT scheme_name, category, return_1yr_pct, return_3yr_pct, "
        "morningstar_rating FROM fact_performance "
        "WHERE return_3yr_pct IS NOT NULL "
        f"ORDER BY return_3yr_pct DESC LIMIT {n}",
        "top performers",
    )


def fetch_top_risk_adjusted(conn, n=5):
    return safe_query(
        conn,
        "SELECT scheme_name, category, sharpe_ratio, return_3yr_pct, "
        "std_dev_ann_pct FROM fact_performance "
        "WHERE sharpe_ratio IS NOT NULL AND return_3yr_pct IS NOT NULL "
        f"ORDER BY sharpe_ratio DESC LIMIT {n}",
        "risk-adjusted leaders",
    )


def fetch_category_flows(conn, n=5):
    latest = safe_query(conn, "SELECT MAX(month) AS m FROM category_inflows", "category month")
    if latest.empty or pd.isna(latest.iloc[0]["m"]):
        return pd.DataFrame(), None
    month = latest.iloc[0]["m"]
    df = safe_query(
        conn,
        "SELECT category, net_inflow_cr FROM category_inflows "
        f"WHERE month = '{month}' ORDER BY net_inflow_cr DESC LIMIT {n}",
        "category flows",
    )
    return df, month


def fetch_fund_house_leaders(conn, n=5):
    latest = safe_query(conn, "SELECT MAX(date) AS d FROM aum_by_fund_house", "fund house date")
    if latest.empty or pd.isna(latest.iloc[0]["d"]):
        return pd.DataFrame(), None
    date = latest.iloc[0]["d"]
    df = safe_query(
        conn,
        "SELECT fund_house, aum_crore, num_schemes FROM aum_by_fund_house "
        f"WHERE date = '{date}' ORDER BY aum_crore DESC LIMIT {n}",
        "fund house leaders",
    )
    return df, date


def fetch_risk_alerts(conn, n=5):
    return safe_query(
        conn,
        "SELECT scheme_name, category, sharpe_ratio, max_drawdown_pct, aum_crore "
        "FROM fact_performance WHERE negative_sharpe_flag = 1 "
        f"ORDER BY aum_crore DESC LIMIT {n}",
        "risk alerts",
    )


def get_subscribers(fallback_email):
    """Fetch the subscriber list from the Supabase cloud database."""
    db_url = os.environ.get("SUPABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    if not db_url:
        print("Supabase URL not found. Using test fallback.")
        return [fallback_email]

    try:
        from sqlalchemy import create_engine
        engine = create_engine(db_url)
        df = pd.read_sql("SELECT email FROM subscribers", engine)
        emails = sorted({e.strip() for e in df["email"].dropna().tolist() if e.strip()})
        if not emails:
            print("Subscribers table is empty in Supabase. Using test fallback.")
            return [fallback_email]
        return emails
    except Exception as e:
        print(f"Error fetching subscribers from Supabase: {e}. Using test fallback.")
        return [fallback_email]


# ---------------------------------------------------------------------------
# HTML building blocks
# ---------------------------------------------------------------------------

def build_table_rows(df, columns, empty_message="Data temporarily unavailable."):
    if df.empty:
        return (
            f'<tr><td colspan="{len(columns)}" style="padding:20px; text-align:center; '
            f'color:#64748b; font-size:13px;">{empty_message}</td></tr>'
        )
    rows = ""
    for i, (_, row) in enumerate(df.iterrows()):
        bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
        cells = ""
        for col in columns:
            raw = row.get(col["key"])
            value = col["fmt"](raw) if col.get("fmt") else raw
            align = col.get("align", "left")
            weight = col.get("weight", 500 if align == "left" else 600)
            color = col.get("color", "#1e293b")
            cells += (
                f'<td style="padding:12px 14px; font-size:13px; color:{color}; '
                f'font-weight:{weight}; text-align:{align}; line-height:1.4;">{value}</td>'
            )
        rows += f'<tr style="background-color:{bg}; border-bottom:1px solid #e2e8f0;">{cells}</tr>'
    return rows


def build_section(title, subtitle, columns, df, empty_message="Data temporarily unavailable."):
    header_cells = "".join(
        f'<th style="padding:10px 14px; font-size:11px; font-weight:700; '
        f'text-transform:uppercase; letter-spacing:0.04em; color:#475569; '
        f'text-align:{c.get("align", "left")}; border-bottom:2px solid #e2e8f0;">{c["header"]}</th>'
        for c in columns
    )
    subtitle_html = (
        f'<p style="margin:2px 0 12px 0; font-size:12px; color:#64748b;">{subtitle}</p>'
        if subtitle else '<div style="margin-bottom:10px;"></div>'
    )
    rows_html = build_table_rows(df, columns, empty_message)
    return f"""
    <h2 style="margin:30px 0 2px 0; font-size:16px; font-weight:700; color:#0f172a;">{title}</h2>
    {subtitle_html}
    <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0; border-radius:8px; border-collapse:separate; border-spacing:0; overflow:hidden;">
        <thead><tr style="background-color:#f8fafc;">{header_cells}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """


def build_bar_chart(df, label_col, value_col, empty_message="Data temporarily unavailable."):
    if df.empty:
        return f'<p style="font-size:13px; color:#64748b;">{empty_message}</p>'
    max_val = df[value_col].max()
    rows = ""
    for _, row in df.iterrows():
        val = row[value_col]
        width_pct = max(int((val / max_val) * 100), 4) if max_val else 4
        label = str(row[label_col])[:28]
        rows += f"""
        <tr>
            <td style="padding:5px 10px 5px 0; font-size:12px; color:#334155; width:170px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{label}</td>
            <td style="padding:5px 0;">
                <table width="100%" cellpadding="0" cellspacing="0"><tr>
                    <td style="background-color:#0284c7; height:10px; border-radius:4px; width:{width_pct}%; font-size:1px; line-height:1px;">&nbsp;</td>
                    <td style="width:{100 - width_pct}%; font-size:1px; line-height:1px;">&nbsp;</td>
                </tr></table>
            </td>
            <td style="padding:5px 0 5px 10px; font-size:12px; font-weight:700; color:#0f172a; text-align:right; width:55px;">{val:.1f}%</td>
        </tr>
        """
    return f'<table width="100%" cellpadding="0" cellspacing="0">{rows}</table>'


def build_stat_card(label, value, sub_html=""):
    return f"""
    <td width="33%" valign="top" style="padding:16px; background-color:#f8fafc; border:1px solid #e2e8f0; border-radius:8px;">
        <p style="margin:0 0 6px 0; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.04em; color:#64748b;">{label}</p>
        <p style="margin:0 0 4px 0; font-size:20px; font-weight:700; color:#0f172a;">{value}</p>
        <div style="font-size:12px;">{sub_html}</div>
    </td>
    """


def build_market_pulse(pulse):
    if not pulse:
        return '<p style="font-size:13px; color:#64748b;">Market pulse data temporarily unavailable.</p>'

    aum_card = build_stat_card(
        f"Industry AUM · {fmt_month(pulse.get('aum_date'))}",
        fmt_crore(pulse.get("aum_latest")),
        change_badge(pulse.get("aum_change_pct")) + ' <span style="color:#94a3b8;">MoM</span>',
    )
    sip_card = build_stat_card(
        f"SIP Inflows · {fmt_month(pulse.get('sip_month'))}",
        fmt_crore(pulse.get("sip_inflow")),
        change_badge(pulse.get("sip_yoy")) + ' <span style="color:#94a3b8;">YoY</span>',
    )
    folio_card = build_stat_card(
        f"Total Folios · {fmt_month(pulse.get('folio_month'))}",
        f"{fmt_num(pulse.get('folios'), 2)} Cr" if pulse.get("folios") is not None else "N/A",
        change_badge(pulse.get("folio_change_pct")) + ' <span style="color:#94a3b8;">MoM</span>',
    )

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0"><tr>
        <td width="8"></td>
        {aum_card}
        <td width="12"></td>
        {sip_card}
        <td width="12"></td>
        {folio_card}
        <td width="8"></td>
    </tr></table>
    """


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def generate_html_report():
    try:
        conn = sqlite3.connect(DB_PATH)
    except Exception as e:
        print(f"Fatal: could not open database ({e}). Sending minimal fallback report.")
        conn = None

    pulse = fetch_market_pulse(conn) if conn else {}
    top_performers = fetch_top_performers(conn) if conn else pd.DataFrame()
    top_risk_adjusted = fetch_top_risk_adjusted(conn) if conn else pd.DataFrame()
    category_flows, category_month = fetch_category_flows(conn) if conn else (pd.DataFrame(), None)
    fund_house_leaders, fh_date = fetch_fund_house_leaders(conn) if conn else (pd.DataFrame(), None)
    risk_alerts = fetch_risk_alerts(conn) if conn else pd.DataFrame()

    if conn:
        conn.close()

    # --- Section: Market pulse ---
    pulse_html = build_market_pulse(pulse)

    # --- Section: Top performers (table + bar chart) ---
    top_perf_cols = [
        {"key": "scheme_name", "header": "Scheme", "align": "left"},
        {"key": "category", "header": "Category", "align": "left", "color": "#64748b", "weight": 400},
        {"key": "return_1yr_pct", "header": "1Y Return", "align": "right", "fmt": fmt_pct},
        {"key": "return_3yr_pct", "header": "3Y CAGR", "align": "right", "fmt": fmt_pct, "color": "#16a34a"},
        {"key": "morningstar_rating", "header": "Rating", "align": "center", "fmt": fmt_stars},
    ]
    top_perf_table = build_section(
        "🏆 Top 5 Performers · 3-Year CAGR",
        "Ranked by annualized 3-year compound growth rate across all tracked schemes.",
        top_perf_cols,
        top_performers,
    )
    top_perf_chart = build_bar_chart(top_performers, "scheme_name", "return_3yr_pct")

    # --- Section: Risk-adjusted leaders ---
    risk_adj_cols = [
        {"key": "scheme_name", "header": "Scheme", "align": "left"},
        {"key": "category", "header": "Category", "align": "left", "color": "#64748b", "weight": 400},
        {"key": "sharpe_ratio", "header": "Sharpe", "align": "right", "fmt": lambda v: fmt_num(v, 2), "color": "#0284c7"},
        {"key": "return_3yr_pct", "header": "3Y CAGR", "align": "right", "fmt": fmt_pct},
        {"key": "std_dev_ann_pct", "header": "Volatility", "align": "right", "fmt": fmt_pct, "color": "#64748b"},
    ]
    risk_adj_table = build_section(
        "⚖️ Best Risk-Adjusted Returns",
        "Highest Sharpe ratios — strongest return delivered per unit of risk taken.",
        risk_adj_cols,
        top_risk_adjusted,
    )

    # --- Section: Category flows ---
    cat_cols = [
        {"key": "category", "header": "Category", "align": "left"},
        {"key": "net_inflow_cr", "header": "Net Inflow", "align": "right", "fmt": fmt_crore, "color": "#16a34a"},
    ]
    category_table = build_section(
        "📊 Where Money Is Flowing",
        f"Net inflows by category for {fmt_month(category_month)}." if category_month else None,
        cat_cols,
        category_flows,
    )

    # --- Section: Fund house leaders ---
    fh_cols = [
        {"key": "fund_house", "header": "Fund House", "align": "left"},
        {"key": "aum_crore", "header": "AUM", "align": "right", "fmt": fmt_crore},
        {"key": "num_schemes", "header": "Schemes", "align": "right", "fmt": lambda v: fmt_num(v, 0), "color": "#64748b", "weight": 400},
    ]
    fh_table = build_section(
        "🏛️ AUM Leaderboard",
        f"Largest fund houses by assets under management as of {fmt_month(fh_date)}." if fh_date else None,
        fh_cols,
        fund_house_leaders,
    )

    # --- Section: Risk alerts ---
    alert_cols = [
        {"key": "scheme_name", "header": "Scheme", "align": "left"},
        {"key": "category", "header": "Category", "align": "left", "color": "#64748b", "weight": 400},
        {"key": "sharpe_ratio", "header": "Sharpe", "align": "right", "fmt": lambda v: fmt_num(v, 2), "color": "#dc2626"},
        {"key": "max_drawdown_pct", "header": "Max Drawdown", "align": "right", "fmt": fmt_pct, "color": "#dc2626"},
        {"key": "aum_crore", "header": "AUM", "align": "right", "fmt": fmt_crore},
    ]
    has_alerts = not risk_alerts.empty
    alert_table = build_section(
        "⚠️ Risk Watchlist",
        "Sizeable schemes currently flagged for negative risk-adjusted returns.",
        alert_cols,
        risk_alerts,
        empty_message="No schemes are currently flagged. All clear.",
    )

    today_str = datetime.now().strftime("%d %B %Y")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bluestock Weekly Analytics</title>
    </head>
    <body style="margin:0; padding:0; background-color:#f1f5f9; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#f1f5f9; padding:20px 0;">
            <tr>
                <td align="center">
                    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width:640px; width:100%; background-color:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03); border:1px solid #e2e8f0;">

                        <!-- Header Banner -->
                        <tr>
                            <td style="background:linear-gradient(135deg, #1e3a8a 0%, #0284c7 100%); padding:32px 24px; text-align:left;">
                                <h1 style="margin:0; color:#ffffff; font-size:24px; font-weight:700; letter-spacing:-0.5px;">Bluestock Intelligence</h1>
                                <p style="margin:4px 0 0 0; color:#bae6fd; font-size:14px; font-weight:400;">Weekly Mutual Fund Performance Briefing · {today_str}</p>
                            </td>
                        </tr>

                        <!-- Body -->
                        <tr>
                            <td style="padding:28px 24px 8px 24px;">
                                <p style="margin:0 0 12px 0; font-size:16px; font-weight:600; color:#0f172a;">Dear Investor,</p>
                                <p style="margin:0 0 20px 0; font-size:15px; line-height:1.6; color:#334155;">
                                    Here's your curated snapshot of the mutual fund industry this week — market-wide flows,
                                    top performers, risk-adjusted leaders, and where the smart money is moving.
                                </p>

                                {pulse_html}

                                {top_perf_table}
                                <div style="margin-top:12px;">{top_perf_chart}</div>

                                {risk_adj_table}

                                {category_table}

                                {fh_table}

                                {alert_table}

                                <!-- CTA -->
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-top:32px; text-align:center;">
                                    <tr>
                                        <td>
                                            <a href="{DASHBOARD_URL}" target="_blank" style="display:inline-block; background-color:#0284c7; color:#ffffff; font-size:14px; font-weight:600; text-decoration:none; padding:12px 28px; border-radius:6px; box-shadow:0 2px 4px rgba(2,132,199,0.2);">
                                                Launch Full Analytics Dashboard
                                            </a>
                                        </td>
                                    </tr>
                                </table>

                                <!-- Info box -->
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-top:24px; margin-bottom:8px; background-color:#f8fafc; border-left:4px solid #0284c7; border-radius:4px;">
                                    <tr>
                                        <td style="padding:14px 16px; font-size:13px; line-height:1.5; color:#475569;">
                                            <strong>Automated Run Notice:</strong> This briefing was generated programmatically from the latest
                                            available data in our warehouse. Figures reflect the most recent reporting period per data source and
                                            may lag real-time by a few days.
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="background-color:#f8fafc; padding:24px; border-top:1px solid #e2e8f0; text-align:center;">
                                <p style="margin:0 0 6px 0; font-size:12px; color:#64748b; font-weight:500;">Bluestock MF Analytics Platform</p>
                                <p style="margin:0; font-size:11px; color:#94a3b8; line-height:1.4;">
                                    You receive these updates because you enrolled in automated reporting via the dashboard.<br>
                                    To alter subscription parameters or opt out, please manage your settings on the terminal.
                                </p>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html, has_alerts


# ---------------------------------------------------------------------------
# Send
# ---------------------------------------------------------------------------

def send_emails():
    sender_email = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")

    if not sender_email or not password:
        print("Missing email credentials environment variables. Exiting.")
        return

    emails = get_subscribers(sender_email)
    html_content, has_alerts = generate_html_report()

    subject = f"Weekly Market Intelligence Briefing | {datetime.now().strftime('%d %b %Y')} | Bluestock Analytics"
    if has_alerts:
        subject = "⚠️ " + subject

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = f"Bluestock Intelligence <{sender_email}>"
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, emails, msg.as_string())
        print(f"Workflow complete. Report sent to {len(emails)} subscriber(s): {emails}")
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    send_emails()