import requests
import numpy as np
import json
import scipy.io.wavfile as wav
from whisperspeech.pipeline import Pipeline

import os



def send_speech_generation_request(text, wav_file_path, profile_name,
                                   server_url='http://localhost:8080/generate_speech'):
    """Send a request to the Flask server to generate speech from text and a speaker WAV sample."""

    try:
        sample_rate, speaker_wav_np_array = wav.read(wav_file_path)
        print(f"WAV file loaded: {wav_file_path}, Sample rate: {sample_rate}, Shape: {speaker_wav_np_array.shape}")
    except Exception as e:
        print(f"Error loading WAV file: {e}")
        return

    speaker_wav_list = speaker_wav_np_array.tolist()

    payload = {
        'text': text,
        'speaker_wav': speaker_wav_list,
        'profile_name': profile_name
    }

    # Send the POST request to the server
    try:
        response = requests.post(server_url, json=payload)
        if response.status_code == 200:
            with open(f"{profile_name}_generated.wav", 'wb') as f:
                f.write(response.content)
            print("Audio file received and saved.")
        else:
            print(f"Error: {response.status_code}, {response.json()}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage:
if __name__ == "__main__":
    text = """
    This is the first demo of Whisper Speech, a fully open source 
    text-to-speech model trained by Collabora and Lion on the Juwels supercomputer.
    """
    # profile_name = "oded"
    #
    speaker_wav_path = r"C:\colman\Final project\Deceptify\WhisperSpeech\oded_voice.wav"
    #
    # send_speech_generation_request(text, speaker_wav_path, profile_name)
    best_model = 't2s-v1.95-small-8lang.model'
    pipe = Pipeline(t2s_ref=f'whisperspeech/whisperspeech:{best_model}',
                    s2a_ref='whisperspeech/whisperspeech:s2a-v1.95-medium-7lang.model')

    output = pipe.generate("""
    This is the first demo of Whisper Speech, a fully open source text-to-speech model trained by Collabora and Lion on the Juwels supercomputer.
    """, lang='en', speaker=speaker_wav_path)

    wav.write("speech.wav", rate=24000, data=output)
    print('done')
