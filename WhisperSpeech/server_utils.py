import os

import numpy as np
from scipy.io.wavfile import write
from email.message import EmailMessage
import ssl
import smtplib
from dotenv import load_dotenv

load_dotenv()

import string
from pydub import AudioSegment


def create_directory_if_not_exists(directory_path):
    """Create a directory if it does not exist."""
    try:
        os.makedirs(directory_path, exist_ok=True)
    except Exception as e:
        print(f"Failed to create directory {directory_path}: {e}")
        raise


def save_speaker_wav_to_dir(speaker_wav_obj, save_wav_path, rate=44100):
    """Save a NumPy array as a WAV file."""
    try:
        scaled = np.int16(speaker_wav_obj / np.max(np.abs(speaker_wav_obj)) * 32767)
        write(save_wav_path, rate, scaled)
        print(f"Wave file saved at {save_wav_path}")
    except Exception as e:
        print(f"Failed to save WAV file: {e}")
        raise


def clean_text(text):
    text = text.replace(" ", "_")
    text = text.translate(str.maketrans('', '', string.punctuation))
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    text = ''.join(c for c in text if c in valid_chars)
    return text.lower()


def convert_wav_to_ogg(wav_filepath, ogg_filepath):
    try:
        audio = AudioSegment.from_wav(wav_filepath)
        audio.export(ogg_filepath, format="ogg")
        os.remove(wav_filepath)
        return ogg_filepath
    except Exception as e:
        print(f'Erro while trying to convert wav to ogg: {e}')
        return None


def send_email(email_receiver, display_name, email_subject, email_body, from_email=None):
    email_sender = os.getenv('MAIL_USERNAME')
    email_password = os.getenv('MAIL_PASSWORD')

    print(f"email_sender {email_sender}\n email_password {email_password}")

    em = EmailMessage()
    if from_email:
        em['from'] = f"{display_name} <{from_email}>"
    else:
        em['from'] = f"{display_name} <{email_sender}>"

    em['to'] = email_receiver
    em['subject'] = email_subject
    em.set_content(email_body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(os.getenv('MAIL_SERVER'), 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
