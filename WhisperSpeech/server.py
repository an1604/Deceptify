import os
import queue
import string
import threading
import time
import uuid

import numpy as np
from flask import Flask, request, jsonify, send_file
import torchaudio
from whisperspeech.pipeline import Pipeline
from scipy.io.wavfile import write
from queue import Queue

# Initialize Flask app
app = Flask(__name__)
speakers = {}
tasks_queue = Queue()  # Q for the voice clone tasks
results = {}  # Dictionary to keep track the results
default_file = os.path.join(os.path.dirname(__file__), 'Drake.mp3')  # File for healthcheck.
stop = threading.Event()

# Load the best model
best_model = 't2s-v1.95-small-8lang.model'
pipe = Pipeline(t2s_ref=f'whisperspeech/whisperspeech:{best_model}',
                s2a_ref='whisperspeech/whisperspeech:s2a-v1.95-medium-7lang.model')


def runner():
    global tasks_queue, results, stop
    print("runner starts in a new thread...")
    while not stop.is_set():
        try:
            task_id, task_data = tasks_queue.get(timeout=5)  # Wake up every 5 seconds to avoid deadlock.
            if task_data is not None:
                print("new task occur, task_id is", task_id)
                text, speaker_wav_path, output_filename = task_data
                output_filename = generate_audio(text, speaker_wav_path, output_filename)
                if output_filename is not None:
                    results[task_id] = output_filename
                    print(f'task {task_id} done and saved in {output_filename}')
        except queue.Empty:
            continue


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
        return output_filename
    except Exception as e:
        print(f"Failed to generate audio: {e}")
        return None


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


def clean_text(text):
    text = text.replace(" ", "_")
    text = text.translate(str.maketrans('', '', string.punctuation))
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    text = ''.join(c for c in text if c in valid_chars)
    return text.lower()


@app.route('/generate_speech', methods=['POST'])
def generate_speech():
    global tasks_queue

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
        output_filename = os.path.join(result_dir_path, f'{clean_text(text)}.wav')  # The future cloned wav file
        speaker_wav_path = os.path.join(result_dir_path, f'{profile_name}_speech.wav')  # The existing wav file

        save_speaker_wav_to_dir(speaker_wav, speaker_wav_path)

        task_id = str(uuid.uuid4())  # Generate a unique task id, to future memorization what to return to whom.
        tasks_queue.put((task_id, (text, speaker_wav_path, output_filename)))
        return jsonify({"task_id": task_id}), 202

    except Exception as e:
        print(f"Error in /generate_speech: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/get_result/<task_id>', methods=['GET'])
def get_result(task_id):
    global results
    if task_id in results:
        output_filename = results.pop(task_id)  # Get and rm the result.
        print(f"for task {task_id} output file is: {output_filename}")
        return send_file(output_filename, as_attachment=True, download_name=os.path.basename(output_filename),
                         mimetype='audio/wav')
    else:
        return jsonify({"status": "pending"}), 202


@app.route('/ping', methods=['GET'])
def ping_server():
    return 'pong', 200


@app.route('/health_check', methods=['GET'])  # Health check.
def health_check():
    global default_file
    try:
        if os.path.exists(default_file):
            return send_file(default_file, as_attachment=True, download_name=os.path.basename(default_file),
                             mimetype='audio/wav')
        else:
            return jsonify({"status": "failed", "reason": "Default file not found"}), 500
    except Exception as e:
        return jsonify({"status": "failed", "reason": str(e)}), 500


if __name__ == "__main__":
    try:
        print("Main run...")
        runner_thread = threading.Thread(target=runner)
        runner_thread.start()
        app.run(host='0.0.0.0', port=8080)
        stop.set()
    except Exception as e:
        stop.set()
        print("Keyboard interrupt received, shutting down...")
