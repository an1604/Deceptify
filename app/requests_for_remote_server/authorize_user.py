import time
import requests
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

URL = os.getenv('SERVER_URL')


def send_validate_code_request(req_id, code):
    response = requests.post(f"{URL}/validate_code", json={
        'req_id': req_id,
        'code': code
    })

    try:
        return response.json().get('authorize')

    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON response. Raw response content:")
        print(response.text)
        print(f"Response status code: {response.status_code}")
        return None


def send_authorize_user_request(email):
    response = requests.post(f'{URL}/authorize_user', json={
        'email': email
    })

    try:
        data = response.json()
        print(data)

        status = data.get('status')

        req_id = data.get('req_id')
        return req_id, status
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON response. Raw response content:")
        print(response.text)
        print(f"Response status code: {response.status_code}")
    except Exception as e:
        print(f"General Exception occur: {e}")


