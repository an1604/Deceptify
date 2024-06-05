from data.prompt import Prompt
import pyaudio
import wave
import requests
from dotenv import load_dotenv
import os

load_dotenv()

SERVER_URL = os.getenv('SERVER_URL')


def add_default_prompts(data_storage):
    if not data_storage.get_prompts():
        print("data storage has no prompts")
        data_storage.add_prompt(Prompt(prompt_desc="Hello", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="Hi", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="Thank you", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="Bye", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="Sorry", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="Why?", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="What did you say?", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="I don't know", is_deletable=False))
        data_storage.add_prompt(Prompt(prompt_desc="what are you talking about", is_deletable=False))


def create_user(username, password):
    try:
        url = f"{SERVER_URL}/data"
        data = {"username": username, "password": password}
        response = requests.post(url, json=data)
        if response.status_code == 409:
            return False
        response.raise_for_status()
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"Server response: {response.text}")
            return False
        return True
    except requests.exceptions.RequestException as e:
        return False


def generate_voice(prompt, description):
    try:
        # Send request to generate voice and get job ID
        url = f"{SERVER_URL}/generate_voice"
        data = {"prompt": prompt, "description": description}
        response = requests.post(url, json=data)
        response.raise_for_status()
        job_id = response.json().get("job_id")

        # Polling the job status
        while True:
            status_url = f"{SERVER_URL}/result/{job_id}"
            status_response = requests.get(status_url)
            if status_response.status_code == 200:
                with open("AudioFiles/" + prompt + ".wav", "wb") as f:
                    f.write(status_response.content)
                return True
            elif status_response.status_code == 202:
                time.sleep(1)  # Wait a second before polling again
            else:
                print("Error", "Failed to retrieve the generated voice.")
                return False
    except requests.exceptions.RequestException as e:
        print(None, "Error", f"Failed to generate voice: {str(e)}")
        return False


def get_device_index(device_name):
    p = pyaudio.PyAudio()
    device_index = None
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if device_name in dev['name']:
            device_index = i
            break
    p.terminate()
    return device_index


def play_audio_through_vbcable(audio_file_path, device_name="CABLE Input"):
    # Open the audio file
    wf = wave.open(audio_file_path, 'rb')
    playback_name = "CABLE Input"
    # Instantiate PyAudio
    p = pyaudio.PyAudio()
    device_index = get_device_index(device_name)
    # Open a stream with the same format as the audio file
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=device_index)

    default_stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
    # Read data in chunks
    chunk = 1024
    data = wf.readframes(chunk)

    # Play the audio file
    while data:
        stream.write(data)
        default_stream.write(data)
        data = wf.readframes(chunk)

    # Stop stream
    stream.stop_stream()
    default_stream.stop_stream()
    stream.close()
    default_stream.close()

    # Close PyAudio
    p.terminate()

    # Close the audio file
    wf.close()
    return True
