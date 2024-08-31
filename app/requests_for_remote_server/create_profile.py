import os
import requests
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

URL = os.getenv('SERVER_URL')


def send_create_profile_request(speaker_wav_path, profile_name):
    with open(speaker_wav_path, 'rb') as f:
        files = {'speaker_wav': f}
        data = {'profile_name': profile_name}

        response = requests.post(f'{URL}/create_speaker_profile', files=files, data=data)

    try:
        return response.json().get('success')
    except requests.exceptions.JSONDecodeError:
        logging.error("Failed to decode JSON response. Raw response content: %s", response.text)
        logging.error("Response status code: %s", response.status_code)
        return None
