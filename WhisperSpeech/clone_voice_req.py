import time
import requests
import numpy as np


def send_speech_generation_request(text, speaker_wav_np_array, profile_name, server_url):
    """Send a request to the Flask server to generate speech from text and a speaker WAV sample."""

    # Convert the NumPy array to a list to make it JSON serializable
    speaker_wav_list = speaker_wav_np_array.tolist()

    # Prepare the data payload
    payload = {
        'text': text,
        'speaker_wav': speaker_wav_list,
        'profile_name': profile_name
    }

    # Send the POST request to the server
    try:
        response = requests.post(server_url, json=payload)

        # Check for a successful request
        if response.status_code == 202:
            print(f"Server accepted the task: {response.json()}")
            return response.json().get('task_id')
        else:
            print(f"Error: {response.status_code}, {response.json()}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Example usage:
if __name__ == "__main__":
    # Example text and profile name
    text = "Hello, this is a generated speech."
    profile_name = "example_profile"

    ip = 'localhost'  # Replace with the actual IP address of the server.
    audio_generation_post_req = f'http://{ip}:8080/generate_speech'
    get_audio_after_gen_req = f'http://{ip}:8080/get_result/{{task_id}}'

    # Example NumPy array representing the WAV file data
    sample_rate = 44100
    t = np.linspace(0., 1., sample_rate)
    speaker_wav_np_array = 0.5 * np.sin(2. * np.pi * 440. * t)  # Simple 440Hz sine wave

    # Send the request
    task_id = send_speech_generation_request(text, speaker_wav_np_array, profile_name, audio_generation_post_req)

    if task_id:
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
