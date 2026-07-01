import sqlite3
import pandas as pd
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_subscribers(sender_email):
    """Fetch all emails from the Supabase cloud database."""
    db_url = os.environ.get("SUPABASE_URL")
    
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    if not db_url:
        print("Supabase URL not found. Using test fallback.")
        return [sender_email]
        
    try:
        from sqlalchemy import create_engine
        engine = create_engine(db_url)
        df = pd.read_sql("SELECT email FROM subscribers", engine)
        emails = df['email'].tolist()
        
        if not emails:
            print("Subscribers table is empty in Supabase. Using test fallback.")
            return [sender_email]
            
        return emails
    except Exception as e:
        print(f"Error fetching subscribers from Supabase: {e}. Using test fallback.")
        return [sender_email]

def generate_html_report():
    """Query the database and build a premium, publication-grade HTML email."""
    try:
        conn = sqlite3.connect("db/bluestock_mf.db")
        query = """
            SELECT scheme_name, category, return_3yr_pct 
            FROM fact_performance 
            WHERE return_3yr_pct IS NOT NULL 
            ORDER BY return_3yr_pct DESC 
            LIMIT 5
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Format returns to look clean (e.g., 18.50%)
        df['return_3yr_pct'] = df['return_3yr_pct'].apply(lambda x: f"{x:.2f}%")
        
        # Rename columns for presentation
        df.columns = ['Mutual Fund Scheme', 'Asset Class', '3-Year CAGR (Return)']
        
        # Build stylized HTML table rows
        table_rows = ""
        for idx, row in df.iterrows():
            bg_color = "#ffffff" if idx % 2 == 0 else "#f8fafc"
            table_rows += f"""
            <tr style="background-color: {bg_color}; border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 14px 16px; font-size: 14px; color: #1e293b; font-weight: 500; line-height: 1.4;">{row['Mutual Fund Scheme']}</td>
                <td style="padding: 14px 16px; font-size: 14px; color: #64748b;">{row['Asset Class']}</td>
                <td style="padding: 14px 16px; font-size: 14px; color: #16a34a; font-weight: 600; text-align: right;">{row['3-Year CAGR (Return)']}</td>
            </tr>
            """
    except Exception as e:
        print(f"Error generating data tables: {e}")
        table_rows = """
        <tr>
            <td colspan="3" style="padding: 20px; text-align: center; color: #64748b;">Data temporarily unavailable. Please visit the live dashboard.</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bluestock Weekly Analytics</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f1f5f9; padding: 20px 0;">
            <tr>
                <td align="center">
                    <!-- Main Container Card -->
                    <table width="100%" max-width="600" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; width: 100%; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03); border: 1px solid #e2e8f0;">
                        
                        <!-- Header Banner -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #1e3a8a 0%, #0284c7 100%); padding: 32px 24px; text-align: left;">
                                <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 700; letter-spacing: -0.5px;">Bluestock Intelligence</h1>
                                <p style="margin: 4px 0 0 0; color: #bae6fd; font-size: 14px; font-weight: 400;">Weekly Mutual Fund Performance Briefing</p>
                            </td>
                        </tr>

                        <!-- Body Content Section -->
                        <tr>
                            <td style="padding: 32px 24px;">
                                <p style="margin: 0 0 12px 0; font-size: 16px; font-weight: 600; color: #0f172a;">Dear Investor,</p>
                                <p style="margin: 0 0 24px 0; font-size: 15px; line-height: 1.6; color: #334155;">
                                    Please find below your curated executive summary highlighting the top-performing mutual funds across our analytics matrix this week, ranked strictly by annualized 3-year compound growth rates (CAGR).
                                </p>

                                <!-- Performance Data Table -->
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="border: 1px solid #e2e8f0; border-radius: 8px; border-collapse: separate; border-spacing: 0; overflow: hidden;">
                                    <thead>
                                        <tr style="background-color: #f8fafc;">
                                            <th style="padding: 12px 16px; font-size: 12px; font-weight: 600; text-transform: uppercase; tracking: 0.05em; color: #475569; text-align: left; border-bottom: 2px solid #e2e8f0;">Mutual Fund Scheme</th>
                                            <th style="padding: 12px 16px; font-size: 12px; font-weight: 600; text-transform: uppercase; tracking: 0.05em; color: #475569; text-align: left; border-bottom: 2px solid #e2e8f0;">Asset Class</th>
                                            <th style="padding: 12px 16px; font-size: 12px; font-weight: 600; text-transform: uppercase; tracking: 0.05em; color: #475569; text-align: right; border-bottom: 2px solid #e2e8f0;">3Y CAGR</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {table_rows}
                                    </tbody>
                                </table>

                                <!-- CTA Section -->
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-top: 32px; text-align: center;">
                                    <tr>
                                        <td>
                                            <a href="https://share.streamlit.io/" target="_blank" style="display: inline-block; background-color: #0284c7; color: #ffffff; font-size: 14px; font-weight: 600; text-decoration: none; padding: 12px 28px; border-radius: 6px; box-shadow: 0 2px 4px rgba(2, 132, 199, 0.2);">
                                                Launch Full Analytics Dashboard
                                            </a>
                                        </td>
                                    </tr>
                                </table>

                                <!-- Informational Info Box -->
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-top: 28px; background-color: #f8fafc; border-left: 4px solid #0284c7; border-radius: 4px;">
                                    <tr>
                                        <td style="padding: 14px 16px; font-size: 13px; line-height: 1.5; color: #475569;">
                                            <strong>Automated Run Notice:</strong> This market summary was programmatically updated via our data orchestration layer. To track historical inflows, run portfolio optimizations, or map capital velocity charts, use the link above.
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Footer Block -->
                        <tr>
                            <td style="background-color: #f8fafc; padding: 24px; border-top: 1px solid #e2e8f0; text-align: center;">
                                <p style="margin: 0 0 6px 0; font-size: 12px; color: #64748b; font-weight: 500;">Bluestock MF Analytics Platform</p>
                                <p style="margin: 0; font-size: 11px; color: #94a3b8; line-height: 1.4;">
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
    return html

def send_emails():
    sender_email = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")

    if not sender_email or not password:
        print("Missing email credentials environment variables. Exiting.")
        return

    emails = get_subscribers(sender_email)
    html_content = generate_html_report()
    
    msg = MIMEMultipart()
    msg['Subject'] = "📊 Weekly Market Intelligence Briefing | Bluestock Analytics"
    msg['From'] = f"Bluestock Intelligence <{sender_email}>"
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, emails, msg.as_string())
        print(f"Workflow Complete! Professional executive report transmitted to: {emails}")
    except Exception as e:
        print(f"Failed to transmit email execution: {e}")

if __name__ == "__main__":
    send_emails()