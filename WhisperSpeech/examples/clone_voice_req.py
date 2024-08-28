import time
import requests

URL = 'http://127.0.0.1:5000'


def send_speech_generation_request(text, profile_name):
    """Send a request to the Flask server to generate speech from text and a speaker WAV sample."""

    # Prepare the data payload
    payload = {
        'text': text,
        'profile_name': profile_name
    }

    # Send the POST request to the server
    try:
        response = requests.post(f'{URL}/generate_speech', json=payload)
        if response.status_code == 202:
            print(f"Server accepted the task: {response.json()}")
            return response.json().get('task_id')
        else:
            print(f"Error: {response.status_code}, {response.json()}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def wait_for_result(task_id):
    if task_id:
        get_audio_after_gen_req = f'{URL}/get_result/{task_id}'
        file_ready = False

        while not file_ready:
            response = requests.get(get_audio_after_gen_req.format(task_id=task_id))
            if response.status_code == 202:
                if response.headers["content-type"].strip().startswith(
                        "application/json"):  # Checks the response format (json or a file)
                    res = response.json()
                    print(f"Response from server received: {res}")
                    if 'status' in res and res['status'] == 'pending':
                        time.sleep(3)  # Waits 3 seconds before checking again.
                else:
                    file_ready = True
                    with open(f"{profile_name}_generated.wav", 'wb') as f:
                        f.write(response.content)
                    print(f"Audio file received and saved as {profile_name}_generated.wav.")
            else:
                print(f"The response from the server is: {response.status_code} with content: {response.content}")
                break
    else:
        print("Failed to send the task to the server.")


if __name__ == "__main__":
    text = "Hello, this is a generated speech."
    profile_name = "Drake"
    task_id = send_speech_generation_request(text, profile_name)

    wait_for_result(task_id)
