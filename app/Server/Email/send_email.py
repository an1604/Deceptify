from email.message import EmailMessage
import ssl
import smtplib

email_sender = 'TheHadar7@gmail.com'
email_password = 'skey dgwb xcop eshf'
email_receiver = 'nataf12386@gmail.com'


def send_email(email_sender, email_password, email_receiver):
    email_subject = 'Hemi'
    email_body = """ 
        Hemi is a very deadly guy
    """
    em = EmailMessage()
    em['from'] = email_sender
    em['to'] = email_receiver
    em['subject'] = email_subject
    em.set_content(email_body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
