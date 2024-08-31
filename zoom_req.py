import json
from datetime import datetime, timedelta
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_meetings_from_zoom(user_id, headers):
    request_url = 'https://api.zoom.us/v2/users/me/meetings'
    response = requests.get(request_url, headers=headers)
    response_json = response.json()

    if response_json.get('meetings'):
        logging.info("Meetings retrieved successfully from Zoom.")
        return response_json.get('meetings')
    else:
        logging.warning("No meetings found for the user.")
    return None


def create_new_meeting(headers, data, user_id='nataf12386@gmail.com'):
    request_url = f'https://api.zoom.us/v2/users/me/meetings'
    response = requests.post(request_url, headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        response_data = response.json()
        logging.info(f"New meeting created successfully: {response_data}")
        start_url = response_data.get('start_url')
        password = response_data.get('password')
        return start_url, password
    else:
        logging.error(f"Failed to create new meeting. Status code: {response.status_code}, Response: {response.text}")
    return None


def generate_data_for_new_meeting(access_token, meeting_name="My Meeting",
                                  year=2024, month=4, day=16, hour=11, minute=11, second=11):
    input_time = datetime(year, month, day, hour, minute, second)
    start_time_str = input_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "topic": meeting_name,
        "type": 2,
        "start_time": start_time_str,
        "duration": "3",
        "settings": {
            "host_video": False,  # CHANGE THIS VALUE TO TURN OFF THE CAMERA ON THE BEGINNING
            "participant_video": True,
            "join_before_host": True,
            "mute_upon_entry": 'true',
            "watermark": 'true',
            "audio": "voip",
            "auto_recording": "cloud"
        }
    }
    logging.info(f"Generated data for new meeting: {data}")
    return headers, data
