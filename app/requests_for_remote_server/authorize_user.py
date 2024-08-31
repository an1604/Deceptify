import time
import requests
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

URL = os.getenv('SERVER_URL')


def send_validate_code_request(req_id, code):
    try:
        response = requests.post(f"{URL}/validate_code", json={
            'req_id': req_id,
            'code': code
        })
        response.raise_for_status()  # Raises an HTTPError for bad responses
        authorization_status = response.json().get('authorize')
        logging.info(f"Authorization status received: {authorization_status}")
        return authorization_status
    except requests.exceptions.JSONDecodeError:
        logging.error("Failed to decode JSON response. Raw response content: %s", response.text)
        logging.error("Response status code: %s", response.status_code)
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request to validate code failed: {e}")
        return None


def send_authorize_user_request(email):
    try:
        response = requests.post(f'{URL}/authorize_user', json={
            'email': email
        })
        response.raise_for_status()
        data = response.json()
        logging.info(f"Authorization data received: {data}")

        status = data.get('status')
        req_id = data.get('req_id')
        return req_id, status
    except requests.exceptions.JSONDecodeError:
        logging.error("Failed to decode JSON response. Raw response content: %s", response.text)
        logging.error("Response status code: %s", response.status_code)
        return None, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request to authorize user failed: {e}")
        return None, None
    except Exception as e:
        logging.error(f"General exception occurred: {e}")
        return None, None
