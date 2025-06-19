import smtplib
import ssl
import os
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json

try:
    import keyring
except ImportError:
    keyring = None

SMTP_SERVER = None
SMTP_PORT = None
SMTP_USERNAME = None
PASSWORD_SERVICE_NAME = "AxisThorn_Agent_SMTP"

def load_email_config(config_file="email_config.json"):
    global SMTP_SERVER, SMTP_PORT, SMTP_USERNAME
    if not os.path.exists(config_file):
        return None
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
            SMTP_SERVER = config.get('smtp_server')
            SMTP_PORT = config.get('smtp_port')
            SMTP_USERNAME = config.get('sender')
            return config
    except:
        return None

def save_email_config(config, config_file="email_config.json"):
    # Don't save password in plain text
    config_to_save = {k: v for k, v in config.items() if k != 'password'}
    with open(config_file, "w") as f:
        json.dump(config_to_save, f, indent=2)

def prompt_email_config():
    global SMTP_SERVER, SMTP_PORT, SMTP_USERNAME
    print("Configure email settings for weekly report delivery:")
    SMTP_SERVER = input("SMTP server (e.g. smtp.gmail.com): ").strip()
    port = input("SMTP port (e.g. 587): ").strip()
    SMTP_PORT = int(port) if port else 587
    SMTP_USERNAME = input("SMTP username (your email address): ").strip()
    password = input("SMTP password (will be stored securely): ").strip()
    
    if keyring:
        try:
            keyring.set_password(PASSWORD_SERVICE_NAME, SMTP_USERNAME, password)
            print("Password stored securely in system keyring.")
        except Exception as e:
            print("Failed to store password in keyring:", e)
            print("WARNING: Password will be stored in memory only.")
            globals()["_PLAINTEXT_PASSWORD"] = password
    else:
        print("WARNING: keyring not available, password will be stored in memory only.")
        globals()["_PLAINTEXT_PASSWORD"] = password
    
    # Save config without password
    config = {
        'sender': SMTP_USERNAME,
        'smtp_server': SMTP_SERVER,
        'smtp_port': SMTP_PORT
    }
    save_email_config(config)
    return config

def send_report(report_file, report_content, recipient="audit@axisthorn.com", config=None):
    global SMTP_SERVER, SMTP_PORT, SMTP_USERNAME
    
    if not config:
        config = load_email_config()
    
    if not (SMTP_SERVER and SMTP_PORT and SMTP_USERNAME):
        print("Email not configured. Skipping email sending.")
        return False
    
    # Get password from keyring or memory
    smtp_password = None
    if keyring:
        smtp_password = keyring.get_password(PASSWORD_SERVICE_NAME, SMTP_USERNAME)
    if not smtp_password:
        smtp_password = globals().get("_PLAINTEXT_PASSWORD")
    
    if not smtp_password:
        print("No SMTP password available. Unable to send email.")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = recipient
        msg['Subject'] = "Weekly Security & Compliance Report - Axis Thorn"
        
        # Add body with summary
        body = "Please find attached the weekly security and compliance report.\n\n"
        # Extract summary from markdown content
        if "End of Report" in report_content:
            body += "Report generated successfully. Please review the attached markdown file for details."
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach report file
        with open(report_file, "rb") as f:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(report_file)}"')
            msg.attach(attachment)
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USERNAME, smtp_password)
            server.send_message(msg)
        
        print(f"Report emailed to {recipient}")
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def setup_email_interactive():
    return prompt_email_config()