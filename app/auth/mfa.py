import os
import pyotp
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Server settings
SMTP_SERVER = os.getenv("MAIL_SERVER")
SMTP_PORT = os.getenv("MAIL_PORT")
SMTP_USERNAME = os.getenv("MAIL_USERNAME")
SMTP_PASSWORD = os.getenv("MAIL_PASSWORD")


def authenticate(onetime_code):
    """
    For now, we assume that all users are authenticated (locally),
    but we need to pass the email to the remote server to perform some checks,
    and then the remote server returns the code to the email in this case.
    """
    try:
        logging.info("Starting authentication process.")
        otp = pyotp.TOTP(onetime_code)
        twofa_code = otp.now()
        logging.info(f"Two-factor authentication code generated successfully: {twofa_code}")
        return twofa_code
    except Exception as e:
        logging.error(f"Error occurred during authentication: {e}")
        return None
