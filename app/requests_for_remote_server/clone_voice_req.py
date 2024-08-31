import os
import time
import requests
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

URL = os.getenv('SERVER_URL')


def send_speech_generation_request(text, profile_name, cps):
    """Send a request to the Flask server to generate speech from text and a speaker WAV sample."""

    # Prepare the data payload
    payload = {
        'text': text,
        'profile_name': profile_name,
        'cps': cps
    }

    # Send the POST request to the server
    try:
        response = requests.post(f'{URL}/generate_speech', json=payload)
        if response.status_code == 202:
            logging.info(f"Server accepted the task: {response.json()}")
            return response.json().get('task_id')
        else:
            logging.error(f"Error: {response.status_code}, {response.json()}")
            return None
    except Exception as e:
        logging.error(f"An error occurred while sending the speech generation request: {e}")
        return None


def wait_for_result(task_id, profile_name, output_filename):
    if task_id:
        requests_counter = 0  # Counting the requests to break the loop if there is a problem with the remote server.
        get_audio_after_gen_req = f'{URL}/get_result/{task_id}'
        file_ready = False

        while not file_ready:
            if requests_counter > 13:
                logging.error("Maximum number of requests reached. Exiting loop.")
                break
            requests_counter += 1

            time.sleep(3)

            try:
                response = requests.get(get_audio_after_gen_req)
                if response.status_code == 200:
                    if response.headers["content-type"].strip().startswith("application/json"):
                        res = response.json()
                        logging.info(f"Response from server received: {res}")
                        if 'status' in res and res['status'] == 'pending':
                            logging.info("Result still pending, retrying...")
                            time.sleep(3)  # Waits 3 seconds before checking again.
                    else:
                        file_ready = True
                        with open(output_filename, 'wb') as f:
                            f.write(response.content)
                        logging.info(f"File {output_filename} successfully written.")
                        return True
                else:
                    logging.error(f"Failed to get result. Status code: {response.status_code}")
            except Exception as e:
                logging.error(f"An error occurred while waiting for the result: {e}")

        logging.error("Failed to retrieve the task result from the server.")
        return False
