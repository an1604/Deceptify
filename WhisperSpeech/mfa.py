import os

import pyotp
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError

load_dotenv()
SMTP_SERVER = os.getenv("MAIL_SERVER")
SMTP_PORT = os.getenv("MAIL_PORT")
SMTP_USERNAME = os.getenv("MAIL_USERNAME")
SMTP_PASSWORD = os.getenv("MAIL_PASSWORD")


def authenticate(email):
    """
    For now, we assume that all users are authenticated (locally),
    but we need to pass the email to the remote server to perform some checks,
    and then the remote serer returns the code to the email in this case.
    """
    try:
        if validate_email(email, check_deliverability=False):
            onetime_code = pyotp.random_base32()
            otp = pyotp.TOTP(onetime_code)
            twofa_code = otp.now()
            return twofa_code
    except (Exception, EmailNotValidError) as e:
        print(e)
        return None
