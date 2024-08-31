import socket
import re
import csv
from io import StringIO
import pyautogui
import scipy.io.wavfile as wav
import numpy as np
import pyaudio
import wave
import requests
from dotenv import load_dotenv
import os
import time
import json
import speech_recognition as sr
from app.requests_for_remote_server.clone_voice_req import send_speech_generation_request, wait_for_result
from app.requests_for_remote_server.create_profile import send_create_profile_request
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SERVER_URL = os.getenv('SERVER_URL')
CLONE_URL = os.getenv('CLONE_URL')
DEFAULT_URL = os.getenv('DEFAULT_URL')


def create_voice_profile(username, profile_name, speaker_wavfile_path):
    try:
        success = send_create_profile_request(profile_name=profile_name, speaker_wav_path=speaker_wavfile_path)
        logging.info(f"Voice profile creation status for '{profile_name}': {success}")
        return success
    except Exception as e:
        logging.error(f"Error creating voice profile: {e}")
        raise e


def clone(text, profile_name_for_tts, output_filename, audios_directory_path, cps):
    try:
        task_id = send_speech_generation_request(text=text, profile_name=profile_name_for_tts, cps=cps)
        if wait_for_result(task_id=task_id, output_filename=output_filename, profile_name=profile_name_for_tts):
            logging.info(f"Cloning successful, output saved as {output_filename}")
            return output_filename
        else:
            logging.warning(f"Cloning failed for text: {text}")
    except Exception as e:
        logging.error(f"Error cloning speech: {e}")
    return None


def get_device_index(device_name):
    p = pyaudio.PyAudio()
    device_index = None
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if device_name in dev['name']:
            device_index = i
            logging.info(f"Device '{device_name}' found at index {device_index}")
            break
    p.terminate()
    if device_index is None:
        logging.error(f"Device '{device_name}' not found.")
    return device_index


def convert_wav_to_pcm(input_path, output_path):
    try:
        sample_rate, data = wav.read(input_path)
        if data.dtype == np.float32:
            max_int16 = np.iinfo(np.int16).max
            data = (data * max_int16).astype(np.int16)
        wav.write(output_path, sample_rate, data)
        logging.info(f"Converted WAV to PCM: {output_path}")
    except Exception as e:
        logging.error(f"Error converting WAV to PCM: {e}")


def play_audio_through_vbcable(audio_file_path, device_name="CABLE Input"):
    try:
        convert_wav_to_pcm(audio_file_path, audio_file_path)
        wf = wave.open(audio_file_path, 'rb')
        p = pyaudio.PyAudio()
        device_index = get_device_index(device_name)
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        output_device_index=device_index)
        chunk = 1024
        data = wf.readframes(chunk)
        while data:
            stream.write(data)
            data = wf.readframes(chunk)
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()
        logging.info(f"Audio played through '{device_name}': {audio_file_path}")
    except Exception as e:
        logging.error(f"Error playing audio: {e}")


def play_background(stop_event, audio_file_path="./AudioFiles/office.wav", device_name="CABLE Input"):
    try:
        wf = wave.open(audio_file_path, 'rb')
        p = pyaudio.PyAudio()
        device_index = get_device_index(device_name)
        if device_index is None:
            raise ValueError(f"Device '{device_name}' not found.")
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        output_device_index=device_index)
        chunk = 1024
        while not stop_event.is_set():
            wf.rewind()
            data = wf.readframes(chunk)
            while data and not stop_event.is_set():
                stream.write(data)
                data = wf.readframes(chunk)
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()
        logging.info(f"Background audio played from {audio_file_path}")
    except Exception as e:
        logging.error(f"Error playing background audio: {e}")


def open_whatsapp():
    pyautogui.press('winleft')
    time.sleep(1)
    pyautogui.write('WHATSAPP')
    time.sleep(2)
    pyautogui.press('enter')
    logging.info("WhatsApp opened.")


def search_contact(contact_name):
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    pyautogui.write(contact_name, interval=0.1)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    contact_x, contact_y = 300, 200
    pyautogui.click(contact_x, contact_y)
    time.sleep(2)
    logging.info(f"Searched and opened chat for contact: {contact_name}")


def start_call():
    call_button_pos = pyautogui.locateCenterOnScreen('API/Photos/CallButton.png')
    if call_button_pos:
        pyautogui.click(call_button_pos)
        logging.info("Call started.")
    else:
        logging.error("Call button not found. Please ensure the image is correct and visible on the screen.")


def end_call():
    end_call_button_pos = pyautogui.locateCenterOnScreen('API/Photos/EndCallButton.png')
    if end_call_button_pos:
        pyautogui.click(end_call_button_pos)
        logging.info("Call ended.")
    else:
        logging.error("End call button not found. Please ensure the image is correct and visible on the screen.")


def ExecuteCall(contact_name, event):
    open_whatsapp()
    search_contact(contact_name)
    start_call()
    logging.info(f"Call executed for contact: {contact_name}")


def transcribe_audio(wav_file_path, json_file_path=None, return_as_string=False):
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_file_path) as audio_file:
        recognizer.adjust_for_ambient_noise(audio_file)
        audio_data = recognizer.record(audio_file)
    try:
        transcription = recognizer.recognize_google(audio_data)
        logging.info(f"Transcription: {transcription}")
        if not return_as_string and json_file_path:
            with open(json_file_path, 'w') as json_file:
                json.dump({"transcription": transcription}, json_file)
            logging.info(f"Transcription saved to {json_file_path}")
        else:
            return transcription
    except sr.UnknownValueError:
        logging.error("Google Web Speech API could not understand the audio")
    except sr.RequestError as e:
        logging.error(f"Could not request results from Google Web Speech API; {e}")


FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024


def record_call(event, fname):
    event.clear()
    logging.info("Recording started...")
    device_index = get_device_index("CABLE Output")
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
    except Exception as e:
        logging.error(f"Error during recording: {e}")
    finally:
        stream.stop_stream()
        logging.info("Recording stopped.")
        stream.close()
        audio.terminate()
        RECORDS_DIR = 'attack_records'
        if not os.path.exists(RECORDS_DIR):
            os.makedirs(RECORDS_DIR)
        WAVE_OUTPUT_FILENAME = os.path.join(RECORDS_DIR, f'{fname}')
        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        logging.info(f"Recording saved: {WAVE_OUTPUT_FILENAME}")


def get_email_from_ip(user_ip):
    return 'admin@example.com'
