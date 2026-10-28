import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
from app.core.config import settings

logger = logging.getLogger("knowiix.email")

def _get_smtp_credentials():
    smtp_user = (os.getenv("SMTP_USER") or getattr(settings, "SMTP_USER", "")).strip('"\'')
    smtp_pass = (os.getenv("SMTP_PASSWORD") or getattr(settings, "SMTP_PASSWORD", "")).strip('"\'').replace(" ", "")
    smtp_host = (os.getenv("SMTP_HOST") or getattr(settings, "SMTP_HOST", "smtp.gmail.com")).strip('"\'')
    smtp_port = int(str(os.getenv("SMTP_PORT") or getattr(settings, "SMTP_PORT", 587)).strip('"\''))
    from_name = (os.getenv("EMAILS_FROM_NAME") or getattr(settings, "EMAILS_FROM_NAME", "Knowiix Security")).strip('"\'')
    return smtp_user, smtp_pass, smtp_host, smtp_port, from_name

def _dispatch_mime_email(to_email: str, subject: str, plain_text: str, html_content: str, email_type_label: str = "Email") -> bool:
    smtp_user, smtp_pass, smtp_host, smtp_port, from_name = _get_smtp_credentials()

    if not smtp_user or not smtp_pass:
        print("[EMAIL ERROR] Gmail SMTP credentials (SMTP_USER/SMTP_PASSWORD) are not set in .env.")
        logger.error("[EMAIL ERROR] Gmail SMTP credentials (SMTP_USER/SMTP_PASSWORD) are not set in .env.")
        return False

    try:
        message = MIMEMultipart("alternative")
        message["From"] = f"{from_name} <{smtp_user}>"
        message["To"] = to_email
        message["Subject"] = subject

        message.attach(MIMEText(plain_text, "plain", "utf-8"))
        message.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
            server.starttls()
            server.login(smtp_user, smtp_pass)
        except Exception as tls_err:
            logger.warning(f"TLS connection failed ({tls_err}), falling back to SSL on port 465")
            server = smtplib.SMTP_SSL(smtp_host, 465, timeout=15)
            server.login(smtp_user, smtp_pass)

        server.sendmail(smtp_user, to_email, message.as_string())
        server.quit()
        print(f"[EMAIL SUCCESS] Dispatched {email_type_label} to {to_email} via Gmail SMTP.")
        logger.info(f"[EMAIL SUCCESS] Dispatched {email_type_label} to {to_email} via Gmail SMTP.")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to dispatch {email_type_label} via Gmail SMTP: {e}")
        logger.error(f"[EMAIL ERROR] Failed to dispatch {email_type_label} via Gmail SMTP: {e}")
        return False

def send_password_reset_otp_email(to_email: str, otp_code: str, user_name: str = "Student") -> bool:
    """
    Sends a beautifully formatted Knowiix dark-themed Password Reset OTP email.
    """
    plain_text = (
        f"Hello {user_name},\n\n"
        f"We received a request to reset your Knowiix password.\n"
        f"Your 6-digit verification code (OTP) is: {otp_code}\n\n"
        f"This code expires in 10 minutes.\n"
        f"If you did not request a password reset, please ignore this email.\n"
    )

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Reset Your Knowiix Password</title>
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
      <div class="brand-title">KNOW<span class="brand-accent">IIX</span></div>
      <p style="margin: 4px 0 0; font-size: 12px; color: #94a3b8;">Learn • Practice • Compete</p>
    </div>
    <div class="body-content">
      <div class="greeting">Hello, {user_name}!</div>
      <p class="text-muted">
        We received a request to reset the password for your Knowiix account associated with <strong>{to_email}</strong>.
        Use the official verification code below to authorize this password reset:
      </p>

      <div class="otp-card">
        <div class="otp-label">Verification Code (OTP)</div>
        <div class="otp-code">{otp_code}</div>
        <div class="expiry-note">Valid for 10 minutes</div>
      </div>

      <div class="security-notice">
        <strong>Security Notice:</strong> If you did not request a password reset, you can safely ignore this email. Your password will remain unchanged, and your account is secure.
      </div>
    </div>
    <div class="footer">
      &copy; 2026 Knowiix Engineering. All rights reserved.<br>
      This is an automated system notification. Please do not reply directly to this email.
    </div>
  </div>
</body>
</html>
"""
    return _dispatch_mime_email(to_email, "Knowiix Password Reset OTP", plain_text, html_content, "Password Reset OTP email")

def send_registration_otp_email(to_email: str, otp_code: str, user_name: str = "Student") -> bool:
    """
    Sends a beautifully formatted Knowiix dark-themed Account Verification OTP email
    to verify new student registration.
    """
    plain_text = (
        f"Hello {user_name}!\n\n"
        f"Welcome to Knowiix - Learn, Practice & Compete!\n"
        f"Your 6-digit account activation code (OTP) is: {otp_code}\n\n"
        f"This code expires in 10 minutes.\n"
        f"Enter this code on the registration page to activate your account and start your placement preparation.\n"
        f"If you did not sign up for Knowiix, please ignore this email.\n"
    )

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Verify Your Knowiix Account</title>
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
      border: 1px solid #10b981;
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
      color: #34d399;
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
    .welcome-pill {{
      display: inline-block;
      padding: 4px 12px;
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.3);
      border-radius: 9999px;
      color: #34d399;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 16px;
    }}
    .security-notice {{
      padding: 16px;
      background-color: #0b1120;
      border-radius: 8px;
      border-left: 3px solid #3b82f6;
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
      <div class="brand-title">KNOW<span class="brand-accent">IIX</span></div>
      <p style="margin: 4px 0 0; font-size: 12px; color: #94a3b8;">Learn • Practice • Compete</p>
    </div>
    <div class="body-content">
      <div class="welcome-pill">New Account Activation</div>
      <div class="greeting">Welcome to Knowiix, {user_name}!</div>
      <p class="text-muted">
        Thank you for creating an account with Knowiix. To activate your account associated with <strong>{to_email}</strong> and start your placement preparation journey, please verify your email address using the official code below:
      </p>

      <div class="otp-card">
        <div class="otp-label">Account Activation Code (OTP)</div>
        <div class="otp-code">{otp_code}</div>
        <div class="expiry-note">Valid for 10 minutes</div>
      </div>

      <div class="security-notice">
        <strong>Getting Started:</strong> Once activated, you will have immediate access to Aptitude placement drives (TCS, Infosys, Accenture, Cognizant), technical coding sandboxes, and scheduled campus assessments.
      </div>
    </div>
    <div class="footer">
      &copy; 2026 Knowiix Engineering. All rights reserved.<br>
      This is an automated system notification. Please do not reply directly to this email.
    </div>
  </div>
</body>
</html>
"""
    return _dispatch_mime_email(to_email, "Knowiix Account Activation OTP", plain_text, html_content, "Registration Activation OTP email")
