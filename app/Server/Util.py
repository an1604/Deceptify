import socket

import pyaudio
import wave
import requests
from dotenv import load_dotenv
import os
import time
import json
import speech_recognition as sr

load_dotenv()

SERVER_URL = os.getenv('SERVER_URL')


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


def createvoice_profile(username, profile_name, file_path):
    """
    Create a new voice profile for the given user.

    Parameters:
    username (str): The username of the user.
    profile_name (str): The name of the new voice profile.
    file_path (str): The path to the audio file for the new voice profile.

    Returns:
    bytes: The server's response content.
    """
    url = f"{SERVER_URL}/voice_profile"
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'username': username, 'profile_name': profile_name}
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        return response.json


def createvideo_profile(username, profile_name, audio_file_path, video_file_path):
    return None
    # TODO: add the video profile creation from the server


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
    with open(file_path, 'wb') as f:
        f.write(response.content)
    return file_path


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
    #                         output=True)
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
        JSON_OUTPUT_FILENAME = os.path.join(RECORDS_DIR, f"{filename}.json")
        WAVE_OUTPUT_FILENAME = os.path.join(RECORDS_DIR, f'{filename}.wav')
        print(WAVE_OUTPUT_FILENAME)
        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

            print(f"{WAVE_OUTPUT_FILENAME} succssfully saved!")
            transcribe_audio(WAVE_OUTPUT_FILENAME, JSON_OUTPUT_FILENAME)
        # TODO: SENT THE RESULT TO THE REMOTE SERVER TO INSPECT THE RESULT!


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
