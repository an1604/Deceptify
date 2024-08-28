import time
import requests
import numpy as np

URL = 'http://127.0.0.1:5000'


def send_validate_code_request(req_id):
    code = input("Enter the code from email:")

    response = requests.post(f"{URL}/validate_code", json={
        'req_id': req_id,
        'code': code
    })

    try:
        print(response.json())
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON response. Raw response content:")
        print(response.text)
        print(f"Response status code: {response.status_code}")


def send_authorize_user_request():
    email = "nataf12386@gmail.com"

    response = requests.post(f'{URL}/authorize_user', json={
        'email': email
    })

    try:
        data = response.json()
        print(data)

        req_id = data.get('req_id')
        send_validate_code_request(req_id)

    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON response. Raw response content:")
        print(response.text)
        print(f"Response status code: {response.status_code}")
    except Exception as e:
        print(f"General Exception occur: {e}")


send_authorize_user_request()
