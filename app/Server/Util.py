import socket
import re
import csv
from io import StringIO
import scipy.io.wavfile as wav
import numpy as np
from threading import Event
import pyaudio
import wave
import requests
from dotenv import load_dotenv
import os
import time
import json
import speech_recognition as sr
from app.Server.run_bark import generateSpeech

load_dotenv()

SERVER_URL = os.getenv('SERVER_URL')


def create_knowledgebase(text):
    pattern = re.compile(r'"Question","Answer".*', re.DOTALL)
    matches = pattern.findall(text)
    if not matches:
        return None
    csv_content = matches[0].strip()
    if os.path.exists('knowledgebase_custom.csv'):
        try:
            os.remove('knowledgebase_custom.csv')
        except Exception as e:
            print(f"An error occurred while trying to delete: {e}")
    else:
        print("file does not exist.")

    with open('knowledgebase_custom.csv', 'w', newline='') as file:
        file.write(csv_content)
        file.close()
    print(csv_content)
    # Get just the relevant question,answer pairs.
    rows = []
    reader = csv.reader(StringIO(csv_content))
    next(reader)  # Skip the header row
    for row in reader:
        if len(row) == 2:
            question, answer = row
            rows.append((question, answer))

    # Rewrite the file with only the question,answer pairs.
    with open('knowledgebase_custom.csv', 'w', newline='') as file:
        file.write("'Question';'Answer'\n")
        for question, answer in rows:
            file.write(f"'{question}';'{answer}'\n")
        with open('Server/LLM/knowledge.csv', 'r') as knowledgebase:
            for line in knowledgebase:
                file.write(line)

    #     file.close()
    return rows


def create_wavs_directory_for_dataset(upload_folder, profile_name="user"):
    profile_directory = os.path.join(upload_folder, profile_name)
    wavs_path = os.path.join(profile_directory, "wavs")
    if not os.path.exists(profile_directory):
        os.makedirs(profile_directory, exist_ok=True)
        os.makedirs(wavs_path, exist_ok=True)
    return wavs_path, profile_directory


def create_csv(wavs_filepath, profile_directory):
    files_and_transcribe = []  # List of tuples (filename, transcribe)
    for file in os.listdir(wavs_filepath):
        if file.lower().endswith('.wav'):
            path = os.path.join(wavs_filepath, file)
            transcript = transcribe_audio(wav_file_path=path, json_file_path=None, return_as_string=True)
            files_and_transcribe.append((file, transcript))

    with open(os.path.join(profile_directory, 'metadata.csv'), 'w') as f:
        for path, transcript in files_and_transcribe:
            line = f"{path}|{transcript}"
            f.write(line + "\n")
    print("File metadata created")


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


def create_voice_profile(username, profile_name, speaker_wavfile_path):
    """
    Create a new voice profile for the given user.

    Parameters:
    username (str): The username of the user.
    profile_name (str): The name of the new voice profile.
    file_path (str): The path to the audio file for the new voice profile.

    Returns:
    bytes: The server's response content.
    """
    url = f"{SERVER_URL}/create_speaker_profile"
    try:
        with open(speaker_wavfile_path, 'rb') as f:
            files = {'file': f}
            data = {'profile_name': profile_name,
                    'speaker_wav': files
                    }
            response = requests.post(url, data=data)
            return response.json().get('success')
    except Exception as e:
        print(f"From create_voice_profile --> {e}")
        raise e


def generate_voice(username, profile_name, prompt):
    """
    Generate a voice clip for the given user and voice profile.

    Parameters:
    username (str): The username of the user.
    profile_name (str): The name of the voice profile.
    prompt (str): The text to be spoken in the voice clip.

    Returns:
    dict: The server's response content as a JSON object.
    """
    url = f"{SERVER_URL}/generate_voice"
    data = {'username': username, 'profile_name': profile_name, 'prompt': prompt}
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()


def get_voice_profile(username, profile_name, prompt, prompt_filename):
    url = f"{SERVER_URL}/voice_profile"
    params = {'username': username, 'profile_name': profile_name, 'prompt_filename': prompt_filename}
    response = requests.get(url, params=params)
    response.raise_for_status()

    file_path = 'Server\\AudioFiles' + '\\' + profile_name + "-" + prompt + ".wav"
    # LOOK ON THIS REGEX FILTERING
    # file_path = re.sub(r'\[.*?\]\s*', '',file_path)

    with open(file_path, 'wb') as f:
        f.write(response.content)
    return file_path


def request_and_wait_for_audio(task_id, profile_name, audios_directory_path):
    get_audio_after_gen_req = f'{SERVER_URL}/get_result/{{task_id}}'
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
                output_filename = os.path.join(audios_directory_path, f"{profile_name}_generated.wav")
                with open(output_filename, 'wb') as f:
                    f.write(response.content)
                print(f"Audio file received and saved as {profile_name}_generated.wav.")
                return output_filename


def clone(text, profile_name_for_tts, output_filename, audios_directory_path):
    default_record = r"C:\Users\adina\PycharmProjects\docker_app\Deceptify_update\app\Server\AudioFiles\Drake.mp3"
    try:
        url = f"{SERVER_URL}/generate_speech"
        response = requests.post(url, data={
            'text': text,
            'profile_name': profile_name_for_tts
        })
        if response.status_code == 202:
            task_id = response.json().get('task_id')
            request_and_wait_for_audio(task_id, profile_name_for_tts, audios_directory_path)
            with open(output_filename, "wb") as output_file:
                output_file.write(response.content)
            print(f"Audio file received and saved as '{output_filename}'")
            return os.path.abspath(output_filename)
        else:
            print(f"An error occurred: {response.json()}")
            return None
            # return default_record
    except (requests.exceptions.RequestException, FileNotFoundError) as e:
        print(f"An error occurred: {e}")
        # For Demo only, return default record
        return default_record


def synthesize(profile_name, prompt):
    try:
        payload = {'text': prompt}
        url = f"{SERVER_URL}/synthesize"
        response = requests.post(url, json=payload)
        print(response.text)
        if response.status_code == 200:
            # Save the received .wav file locally
            with open('AudioFiles' + '\\' + profile_name + "-" + prompt + ".wav", "wb") as f:
                f.write(response.content)
            print("Audio file received and saved")
        else:
            print(f"An error occurred: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


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


def convert_wav_to_pcm(input_path, output_path):
    sample_rate, data = wav.read(input_path)
    if data.dtype == np.float32:
        # Convert floating point data to 16-bit PCM
        max_int16 = np.iinfo(np.int16).max
        data = (data * max_int16).astype(np.int16)
    wav.write(output_path, sample_rate, data)


def play_audio_through_vbcable(audio_file_path, device_name="CABLE Input"):
    # Open the audio file
    convert_wav_to_pcm(audio_file_path, audio_file_path)
    wf = wave.open(audio_file_path, 'rb')
    playback_name = "CABLE Output"
    # Instantiate PyAudio
    p = pyaudio.PyAudio()
    device_index = get_device_index(device_name)
    # Open a stream with the same format as the audio file
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=device_index)

    # default_stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
    #                         channels=wf.getnchannels(),
    #                         rate=wf.getframerate(),
    #                         speakers=True)
    # Read data in chunks
    chunk = 1024
    data = wf.readframes(chunk)

    # Play the audio file
    while data:
        stream.write(data)
        # default_stream.write(data)
        data = wf.readframes(chunk)

    # Stop stream
    stream.stop_stream()
    # default_stream.stop_stream()
    stream.close()
    # default_stream.close()

    # Close PyAudio
    p.terminate()

    # Close the audio file
    wf.close()


def play_background(stop_event, audio_file_path="./AudioFiles/office.wav", device_name="CABLE Input"):
    # Open the audio file
    wf = wave.open(audio_file_path, 'rb')
    playback_name = "CABLE Output"

    # Instantiate PyAudio
    p = pyaudio.PyAudio()
    device_index = get_device_index(device_name)

    if device_index is None:
        raise ValueError(f"Device '{device_name}' not found.")

    # Open a stream with the same format as the audio file
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=device_index)

    chunk = 1024

    while not stop_event.is_set():
        # Reset file position to start
        wf.rewind()
        data = wf.readframes(chunk)

        # Play the audio file
        while data and not stop_event.is_set():
            stream.write(data)
            data = wf.readframes(chunk)

    # Stop stream
    stream.stop_stream()
    stream.close()

    # Close PyAudio
    p.terminate()

    # Close the audio file
    wf.close()


# Whatsapp open and close function

def open_whatsapp():
    pyautogui.press('winleft')
    time.sleep(1)
    pyautogui.write('WHATSAPP')
    time.sleep(2)
    pyautogui.press('enter')


def search_contact(contact_name):
    # Click on the search bar (Ctrl + F)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    # Type the contact name
    pyautogui.write(contact_name, interval=0.1)
    time.sleep(1)
    # Press enter to select the contact
    pyautogui.press('enter')
    time.sleep(1)
    contact_x = 300  # Adjust this value
    contact_y = 200  # Adjust this value

    # Click on the contact in the search results to open the chat
    pyautogui.click(contact_x, contact_y)
    time.sleep(2)  # Wait for the chat to open


def start_call():
    # Click on the call button (assuming the call button is in a consistent position relative to the window)
    call_button_pos = pyautogui.locateCenterOnScreen('API/'
                                                     'Photos/CallButton.png')  # Use an image of the call button
    if call_button_pos:
        pyautogui.click(call_button_pos)
    else:
        print("Call button not found. Please ensure the image is correct and visible on the screen.")


def end_call():
    end_call_button_pos = pyautogui.locateCenterOnScreen('API/Photos/EndCallButton.png')
    if end_call_button_pos:
        pyautogui.click(end_call_button_pos)
    else:
        print("End call button not found. Please ensure the image is correct and visible on the screen.")


def ExecuteCall(contact_name, event):
    open_whatsapp()
    search_contact(contact_name)
    start_call()
    # event.wait()
    # end_call()


FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024


def transcribe_audio(wav_file_path, json_file_path=None, return_as_string=False):
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_file_path) as audio_file:
        recognizer.adjust_for_ambient_noise(audio_file)
        audio_data = recognizer.record(audio_file)

    try:
        transcription = recognizer.recognize_google(audio_data)
        print(f"Transcription: {transcription}")
        if not return_as_string and json_file_path:
            with open(json_file_path, 'w') as json_file:
                json.dump({"transcription": transcription}, json_file)
            print(f"Transcription saved to {json_file_path}")
        else:
            return transcription

    except sr.UnknownValueError:
        print("Google Web Speech API could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech API; {e}")


def record_call(event, fname):
    event.clear()
    print("Recording...")
    time.sleep(10)
    # stopped = session['stopped call']
    # print(stopped + "-1")
    playback_name = "CABLE Output"
    device_index = get_device_index(playback_name)
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=device_index)

    frames = []
    try:
        while not event.is_set():
            frames.append(stream.read(CHUNK))
            # stopped = session['stopped call']
    except Exception as e:
        print(e)
    finally:
        stream.stop_stream()
        print("stopped recording...")
        stream.close()
        audio.terminate()

        # Save the record in a unique directory.
        RECORDS_DIR = 'attack_records'
        if not os.path.exists(RECORDS_DIR):
            os.makedirs(RECORDS_DIR)

        # Initialize the file names for both transcript and record.
        filename = fname

        # Saving both JSON and WAV in the same name, in the same directory.
        WAVE_OUTPUT_FILENAME = os.path.join(RECORDS_DIR, f'{filename}')
        print(WAVE_OUTPUT_FILENAME)
        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

            print(f"{WAVE_OUTPUT_FILENAME} succssfully saved!")


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def get_email_from_ip(user_ip):
    """
    In this case, we want to ask the remote server for email given IP address.
    To make sure the authentication is properly.
    """
    return 'admin@example.com'


if __name__ == '__main__':
    abc = Event()
    play_background(abc)
