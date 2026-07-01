import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_subscribers(sender_email):
    """Fetch all emails from the Supabase cloud database."""
    db_url = os.environ.get("SUPABASE_URL")
    
    # SQLAlchemy requires the prefix to be postgresql://
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    if not db_url:
        print("Supabase URL not found. Using test fallback.")
        return [sender_email]
        
    try:
        # Connect to Supabase
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
    """Query the database and build a stylized HTML table."""
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
        
        # Build an elegant HTML table using inline CSS styling
        table_html = df.to_html(index=False, classes='report-table')
        # Inject standard clean styling into the table raw string
        table_html = table_html.replace(
            'class="dataframe report-table"', 
            'style="width:100%; border-collapse:collapse; font-family:Arial; margin-top:15px;"'
        ).replace(
            '<th>', '<th style="background-color:#2E86C1; color:white; padding:10px; border:1px solid #ddd; text-align:left;">'
        ).replace(
            '<td>', '<td style="padding:10px; border:1px solid #ddd; text-align:left;">'
        )
    except Exception as e:
        print(f"Error generating data tables: {e}")
        table_html = "<p>Data temporarily unavailable. Please visit the dashboard.</p>"

    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
            <h2 style="color: #2E86C1; border-bottom: 2px solid #2E86C1; padding-bottom: 10px; margin-top: 0;">Bluestock MF Weekly Insights 📈</h2>
            <p>Hello,</p>
            <p>Here are the top 5 performing mutual funds for this week based on 3-Year CAGR performance:</p>
            {table_html}
            <br>
            <p style="background-color: #f9f9f9; padding: 10px; border-left: 4px solid #2E86C1; font-size: 14px;">
                <strong>Note:</strong> This is an automated dynamic report generated directly from your GitHub Actions pipeline.
            </p>
            <p>Log back into your live Streamlit dashboard to explore advanced interactive charts, portfolio optimizations, and deeper metrics.</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 11px; color: #777; text-align: center;">
                You are receiving this because you signed up via the Bluestock Dashboard subscription portal.<br>
                To unsubscribe, simply reply to this email.
            </p>
        </body>
    </html>
    """
    return html

def send_emails():
    # Safely pull credentials from the GitHub workflow environment variables
    sender_email = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")

    if not sender_email or not password:
        print("Missing email credentials environment variables. Exiting.")
        return

    # Get subscriber list (or our fallback test address)
    emails = get_subscribers(sender_email)
    html_content = generate_html_report()
    
    msg = MIMEMultipart()
    msg['Subject'] = "📈 Your Weekly Bluestock MF Performance Report"
    msg['From'] = sender_email
    msg.attach(MIMEText(html_content, 'html'))

    try:
        # Secure SMTP SSL connection to Gmail on port 465
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            # Use BCC array to safely blast the emails without leaking recipient addresses
            server.sendmail(sender_email, emails, msg.as_string())
        print(f"Successfully executed workflow! Emailed report sent out to: {emails}")
    except Exception as e:
        print(f"Failed to transmit email execution: {e}")

if __name__ == "__main__":
    send_emails()