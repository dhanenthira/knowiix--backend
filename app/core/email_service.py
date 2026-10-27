import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
from app.core.config import settings

logger = logging.getLogger("codearena.email")

def send_password_reset_otp_email(to_email: str, otp_code: str, user_name: str = "Student") -> bool:
    """
    Sends a beautifully formatted CodeArena dark-themed Password Reset OTP email
    via Gmail SMTP (smtp.gmail.com:587) using the configured App Password.
    Strictly delivers to the email recipient and never prints OTP to the console/terminal.
    """
    smtp_user = (os.getenv("SMTP_USER") or getattr(settings, "SMTP_USER", "")).strip('"\'')
    smtp_pass = (os.getenv("SMTP_PASSWORD") or getattr(settings, "SMTP_PASSWORD", "")).strip('"\'')
    smtp_host = (os.getenv("SMTP_HOST") or getattr(settings, "SMTP_HOST", "smtp.gmail.com")).strip('"\'')
    smtp_port = int(str(os.getenv("SMTP_PORT") or getattr(settings, "SMTP_PORT", 587)).strip('"\''))
    from_name = (os.getenv("EMAILS_FROM_NAME") or getattr(settings, "EMAILS_FROM_NAME", "CodeArena Security")).strip('"\'')

    if not smtp_user or not smtp_pass:
        logger.error("❌ Gmail SMTP credentials (SMTP_USER/SMTP_PASSWORD) are not set in .env.")
        return False

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Reset Your CodeArena Password</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #0b1120;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #e2e8f0;
    }}
    .email-container {{
      max-width: 540px;
      margin: 32px auto;
      background-color: #111827;
      border: 1px solid #1f2937;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }}
    .header {{
      padding: 28px 32px;
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      border-bottom: 1px solid #1f2937;
      text-align: center;
    }}
    .brand-title {{
      font-size: 22px;
      font-weight: 900;
      letter-spacing: 1.5px;
      color: #f8fafc;
      margin: 0;
    }}
    .brand-accent {{
      color: #3b82f6;
    }}
    .body-content {{
      padding: 32px;
    }}
    .greeting {{
      font-size: 18px;
      font-weight: 700;
      color: #f8fafc;
      margin-bottom: 12px;
    }}
    .text-muted {{
      font-size: 14px;
      line-height: 1.6;
      color: #94a3b8;
      margin-bottom: 24px;
    }}
    .otp-card {{
      background: #0f172a;
      border: 1px solid #2563eb;
      border-radius: 12px;
      padding: 20px;
      text-align: center;
      margin: 24px 0;
    }}
    .otp-label {{
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      color: #60a5fa;
      margin-bottom: 8px;
    }}
    .otp-code {{
      font-size: 34px;
      font-weight: 800;
      letter-spacing: 8px;
      color: #ffffff;
      font-family: 'Courier New', Courier, monospace;
    }}
    .expiry-note {{
      font-size: 12px;
      color: #f59e0b;
      margin-top: 10px;
    }}
    .security-notice {{
      padding: 16px;
      background-color: #0b1120;
      border-radius: 8px;
      border-left: 3px solid #f59e0b;
      font-size: 12px;
      color: #cbd5e1;
      line-height: 1.5;
    }}
    .footer {{
      padding: 20px 32px;
      background-color: #0b1120;
      border-top: 1px solid #1f2937;
      text-align: center;
      font-size: 11px;
      color: #64748b;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <div class="brand-title">CODE<span class="brand-accent">ARENA</span></div>
      <p style="margin: 4px 0 0; font-size: 12px; color: #94a3b8;">Learn • Practice • Compete</p>
    </div>
    <div class="body-content">
      <div class="greeting">Hello, {user_name}!</div>
      <p class="text-muted">
        We received a request to reset the password for your CodeArena account associated with <strong>{to_email}</strong>.
        Use the official verification code below to authorize this password reset:
      </p>

      <div class="otp-card">
        <div class="otp-label">Verification Code (OTP)</div>
        <div class="otp-code">{otp_code}</div>
        <div class="expiry-note">⏱ Valid for 10 minutes</div>
      </div>

      <div class="security-notice">
        <strong>Security Notice:</strong> If you did not request a password reset, you can safely ignore this email. Your password will remain unchanged, and your account is secure.
      </div>
    </div>
    <div class="footer">
      &copy; 2026 CodeArena Engineering. All rights reserved.<br>
      This is an automated system notification. Please do not reply directly to this email.
    </div>
  </div>
</body>
</html>
"""

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{otp_code} is your CodeArena Password Reset Code"
        msg["From"] = f"{from_name} <{smtp_user}>"
        msg["To"] = to_email

        plain_text = f"Your CodeArena password reset code is: {otp_code}. It expires in 10 minutes."
        msg.attach(MIMEText(plain_text, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to_email], msg.as_string())

        logger.info(f"✅ Dispatched Password Reset email to {to_email} via Gmail SMTP.")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to dispatch email via Gmail SMTP: {e}")
        return False
