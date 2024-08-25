import os
import numpy as np
from flask import Flask, request, jsonify, send_file
import torchaudio
from whisperspeech.pipeline import Pipeline
from scipy.io.wavfile import write

import requests

external_ip = requests.get('https://ipv4.icanhazip.com').text.strip()
print(f"External IPv4 Address: {external_ip}")

# Initialize Flask app
app = Flask(__name__)
speakers = {}

# Load the best model
best_model = 't2s-v1.95-small-8lang.model'
pipe = Pipeline(t2s_ref=f'whisperspeech/whisperspeech:{best_model}',
                s2a_ref='whisperspeech/whisperspeech:s2a-v1.95-medium-7lang.model')


def add_speaker(profile_name, directory_path, speaker_sample_path):
    global speakers
    if profile_name not in speakers:
        speakers[profile_name] = {
            'speech_dir_path': directory_path,
            'speaker_sample_path': speaker_sample_path
        }


def generate_audio(text, speaker_wav_path, output_filename, sample_rate=24000):
    """Generate audio using the WhisperSpeech model."""
    try:
        audio = pipe.generate(text, lang='en', cps=10.5, speaker=speaker_wav_path)
        generated_audio_cpu = audio.cpu()
        torchaudio.save(output_filename, generated_audio_cpu, sample_rate)
        print(f"Audio saved in {output_filename}")
    except Exception as e:
        print(f"Failed to generate audio: {e}")
        raise


def create_directory_if_not_exists(directory_path):
    """Create a directory if it does not exist."""
    try:
        os.makedirs(directory_path, exist_ok=True)
    except Exception as e:
        print(f"Failed to create directory {directory_path}: {e}")
        raise


def save_speaker_wav_to_dir(speaker_wav_obj, save_wav_path, rate=44100):
    """Save a NumPy array as a WAV file."""
    try:
        scaled = np.int16(speaker_wav_obj / np.max(np.abs(speaker_wav_obj)) * 32767)
        write(save_wav_path, rate, scaled)
        print(f"Wave file saved at {save_wav_path}")
    except Exception as e:
        print(f"Failed to save WAV file: {e}")
        raise


@app.route('/generate_speech', methods=['POST'])
def generate_speech():
    """Endpoint for generating speech from text and speaker wav."""
    try:
        data = request.get_json()

        # Validate input data
        text = data.get('text')
        speaker_wav = data.get('speaker_wav')
        profile_name = data.get('profile_name')

        if not text or not speaker_wav or not profile_name:
            return jsonify({"error": "Missing required fields: text, speaker_wav, profile_name"}), 400

        result_dir_path = os.path.join('output', profile_name)
        create_directory_if_not_exists(result_dir_path)
        output_filename = os.path.join(result_dir_path, f"{text.replace(' ', '_')}.wav")
        speaker_wav_path = os.path.join(result_dir_path, f'{profile_name}_speech.wav')

        save_speaker_wav_to_dir(speaker_wav, speaker_wav_path)
        generate_audio(text, speaker_wav_path, output_filename)

        return send_file(output_filename, as_attachment=True, download_name=os.path.basename(output_filename),
                         mimetype='audio/wav')

    except Exception as e:
        print(f"Error in /generate_speech: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/ping')
def ping():
    return jsonify({"ping": "pong"}), 200


if __name__ == "__main__":
    print("Server run and listen to port 8080...")
    app.run(host='0.0.0.0', port=8080)
