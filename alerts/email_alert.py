import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL = "rudranilmallik720@gmail.com"
PASSWORD = "tnct vwkj qttc uxkv"
TO_EMAIL = "rudranilmallik720@gmail.com"

def send_email_alert(txn, risk, reason):
    body = f"""
    FRAUD ALERT 🚨

    Amount: {txn['amount']}
    Risk Score: {risk:.1f}
    Decision: BLOCK
    Reason: {reason}
    """

    msg = MIMEText(body)
    msg["Subject"] = "🚨 Fraud Alert Detected"
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
    print("Alert email sent.")