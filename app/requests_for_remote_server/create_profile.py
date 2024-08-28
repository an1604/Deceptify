import os

import requests
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv('SERVER_URL')


def send_create_profile_request(speaker_wav_path, profile_name):
    with open(speaker_wav_path, 'rb') as f:
        # Prepare the files dictionary to send the file
        files = {'speaker_wav': f}
        # Prepare the data dictionary to send additional data
        data = {'profile_name': profile_name}

        # Send the POST request with files and data
        response = requests.post(f'{URL}/create_speaker_profile', files=files, data=data)

    try:
        return response.json().get('success')
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON response. Raw response content:")
        print(response.text)
        print(f"Response status code: {response.status_code}")
        return None
