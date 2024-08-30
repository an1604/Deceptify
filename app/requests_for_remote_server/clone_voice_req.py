import os
import time
import requests
import os
import time

from dotenv import load_dotenv

load_dotenv()

URL = os.getenv('SERVER_URL')


def send_speech_generation_request(text, profile_name, cps,regenerate):
    """Send a request to the Flask server to generate speech from text and a speaker WAV sample."""

    # Prepare the data payload
    payload = {
        'text': text,
        'profile_name': profile_name,
        'cps': cps
    }

    url = f'{URL}/generate_speech' if not regenerate else f'{URL}/regenerate_audio'
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 202:
            print(f"Server accepted the task: {response.json()}")
            return response.json().get('task_id')
        else:
            print(f"Error: {response.status_code}, {response.json()}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def wait_for_result(task_id, profile_name, output_filename):
    if task_id:
        requests_counter = 0  # Counting the requests for break the loop if there is a problem in the remote server.
        get_audio_after_gen_req = f'{URL}/get_result/{task_id}'
        file_ready = False

        while not file_ready:
            if requests_counter > 13:
                break
            requests_counter += 1

            time.sleep(3)

            response = requests.get(get_audio_after_gen_req.format(task_id=task_id))
            if response.status_code == 200:
                if response.headers["content-type"].strip().startswith(
                        "application/json"):  # Checks the response format (json or a file)
                    res = response.json()
                    print(f"Response from server received: {res}")
                    if 'status' in res and res['status'] == 'pending':
                        time.sleep(3)  # Waits 3 seconds before checking again.
                else:
                    file_ready = True
                    with open(output_filename, 'wb') as f:
                        f.write(response.content)
                    return True
        print("Failed to send the task to the server.")
        return False
