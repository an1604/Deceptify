import os.path
import queue
import threading
import uuid
import logging

from flask import Flask, request, jsonify, send_file, redirect
import torchaudio
from whisperspeech.pipeline import Pipeline
from queue import Queue

from WhisperSpeech.llm_service import llm_factory
from server_utils import *
from mfa import *

# Initialize Flask app
app = Flask(__name__)
tasks_queue = Queue()  # Q for the voice clone tasks

llm_tasks_queue = Queue()
llm_tasks_map = {}

results = {}  # Dictionary to keep track of the results
authorization_req = {}
default_file = os.path.join(os.path.dirname(__file__), 'speakers/Drake/Drake.mp3')  # File for health check.
stop = threading.Event()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', handlers=[
    logging.FileHandler("server.log"),
    logging.StreamHandler()
])

# Load the best model
best_model = 't2s-v1.95-small-8lang.model'
pipe = Pipeline(t2s_ref=f'whisperspeech/whisperspeech:{best_model}',
                s2a_ref='whisperspeech/whisperspeech:s2a-v1.95-medium-7lang.model')


def runner_for_llm():
    global stop, llm_tasks_queue, results, llm_tasks_map
    logging.info("LLM runner thread started.")

    while not stop.is_set():
        try:
            task_id, prompt = llm_tasks_queue.get(timeout=1)
            logging.info(f"Processing LLM task with task_id: {task_id}, prompt: {prompt}")

            if task_id is not None:
                llm = llm_tasks_map.get(task_id)
                if llm is not None:
                    answer = llm.get_answer(prompt)
                    with threading.Lock():
                        results[task_id] = answer
                    logging.info(f"Answer generated for task_id: {task_id}")
        except queue.Empty:
            continue
        except Exception as e:
            logging.error(f"Error in LLM runner: {e}")


def runner_for_audio():
    global tasks_queue, results, stop
    logging.info("Audio runner thread started.")

    while not stop.is_set():
        try:
            task_id, task_data = tasks_queue.get(timeout=1)
            if task_data is not None:
                logging.info(f"New audio generation task started, task_id: {task_id}")

                text, speaker_wav_path, output_filename, cps = task_data
                logging.info(
                    f"Data from task {task_id}: Text: {text}, speaker_wav_path: {speaker_wav_path}, output_filename: {output_filename}")

                if not os.path.exists(output_filename):
                    output_filename = generate_audio(text, speaker_wav_path, output_filename, cps)

                if output_filename is not None:
                    with threading.Lock():
                        results[task_id] = output_filename
                    logging.info(f'Task {task_id} completed and audio saved at {output_filename}')
        except queue.Empty:
            continue
        except Exception as e:
            logging.error(f"Error in audio runner: {e}")


def generate_audio(text, speaker_wav_path, output_filename, cps=11.5, sample_rate=24000):
    """Generate audio using the WhisperSpeech model."""
    try:
        logging.info(f"Generating audio for text: {text}, speaker_wav_path: {speaker_wav_path}")
        audio = pipe.generate(text, lang='en', cps=cps, speaker=speaker_wav_path)
        generated_audio_cpu = audio.cpu()
        torchaudio.save(output_filename, generated_audio_cpu, sample_rate)
        logging.info(f"Audio saved in {output_filename}")
        return output_filename
    except Exception as e:
        logging.error(f"Failed to generate audio: {e}")
        return None


@app.route('/create_speaker_profile', methods=['POST'])
def create_speaker_profile():
    logging.info("Received request to create speaker profile.")

    if 'speaker_wav' not in request.files or 'profile_name' not in request.form:
        logging.warning("Missing required fields: speaker_wav, profile_name")
        return jsonify({"error": "Missing required fields: speaker_wav, profile_name"}), 400

    speaker_wav = request.files['speaker_wav']
    profile_name = request.form['profile_name']

    profile_result_dir_path = os.path.join('speakers', profile_name)
    create_directory_if_not_exists(profile_result_dir_path)

    speaker_wav_path = os.path.join(profile_result_dir_path, f'{profile_name}_original_speech.wav')
    speaker_wav.save(speaker_wav_path)

    if os.path.exists(profile_result_dir_path) and os.path.exists(speaker_wav_path):
        logging.info(f"Profile {profile_name} created successfully.")
        return jsonify({"success": True}), 200

    logging.error(f"Failed to create profile {profile_name}.")
    return jsonify({"success": False}), 400


@app.route('/generate_speech', methods=['POST'])
def generate_speech():
    global tasks_queue
    logging.info("Received request to generate speech.")
    try:
        data = request.get_json()
        text = data.get('text')
        profile_name = data.get('profile_name')
        cps = data.get('cps')

        if not text or not profile_name:
            logging.warning("Missing required fields: text, profile_name")
            return jsonify({"error": "Missing required fields: text, profile_name"}), 400

        result_dir_path = os.path.join('speakers', profile_name)
        output_filename = os.path.join(result_dir_path, f'{clean_text(text)}.wav')
        speaker_wav_path = os.path.join(result_dir_path, f'{profile_name}_original_speech.wav')

        task_id = str(uuid.uuid4())  # Generate a unique task id.
        tasks_queue.put((task_id, (text, speaker_wav_path, output_filename, cps)))
        logging.info(f"Task {task_id} created for generating speech.")
        return jsonify({"task_id": task_id}), 202

    except Exception as e:
        logging.error(f"Error in /generate_speech: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/get_result/<task_id>', methods=['GET'])
def get_result(task_id):
    logging.info(f"Received request to get result for task_id: {task_id}")
    global results
    if task_id in results:
        output_filename = results.pop(task_id)  # Get and remove the result.
        logging.info(f"Task {task_id} completed. Returning file {output_filename}.")
        return send_file(output_filename, as_attachment=True, download_name=os.path.basename(output_filename),
                         mimetype='audio/wav')
    else:
        logging.info(f"Task {task_id} is still pending.")
        return jsonify({"status": "pending"}), 202


@app.route('/ping', methods=['GET'])
def ping_server():
    logging.info("Ping request received.")
    return 'pong', 200  # Ensure no authentication is applied


@app.route('/health_check', methods=['GET'])  # Health check.
def health_check():
    logging.info("Health check request received.")
    global default_file
    try:
        if os.path.exists(default_file):
            logging.info("Health check file found, returning file.")
            return send_file(default_file, as_attachment=True, download_name=os.path.basename(default_file),
                             mimetype='audio/wav')
        else:
            logging.warning("Health check failed: Default file not found.")
            return jsonify({"status": "failed", "reason": "Default file not found"}), 500
    except Exception as e:
        logging.error(f"Health check error: {e}")
        return jsonify({"status": "failed", "reason": str(e)}), 500


@app.route('/authorize_user', methods=['POST'])
def authorize_login():
    global authorization_req

    logging.info("Authorize user request received.")
    email = request.json.get('email')
    otp_code = authenticate(email)
    logging.info(f"OTP code: {otp_code}")

    if otp_code:
        send_email(email_receiver=email, email_subject="Your 2FA code", email_body=f"Your 2FA code is {otp_code}",
                   display_name="Deceptify Admin", from_email="DeceptifyAdmin<Do Not Reply>@gmail.com")
        req_id = str(uuid.uuid4())
        authorization_req[req_id] = otp_code

        logging.info(f"2FA code sent to {email}. Request ID: {req_id}")
        return jsonify({"status": "success", "req_id": req_id}), 200

    logging.error(f"Failed to send 2FA code to {email}.")
    return jsonify({"status": "failed"}), 500


@app.route('/validate_code', methods=['POST'])
def validate_code():
    logging.info("Validate code request received.")
    global authorization_req

    req_id = request.json.get('req_id')
    code = request.json.get('code')

    if req_id in authorization_req:
        if code == authorization_req.pop(req_id):
            logging.info(f"Code validated successfully for request ID: {req_id}")
            return jsonify({'authorize': True}), 200
        logging.warning(f"Invalid code for request ID: {req_id}")
        return jsonify({'authorize': False}), 200
    logging.error(f"Request ID not found: {req_id}")
    return jsonify({'status': "Cannot find your request."}), 500


@app.route("/new_attack", methods=['POST'])
def new_attack():
    logging.info("Received request to initiate a new attack.")
    mimic_name = request.json.get('mimic_name')
    attack_purpose = request.json.get('attack_purpose')

    llm = llm_factory.generate_new_attack(attack_purpose, mimic_name)
    task_id = str(uuid.uuid4())
    llm_tasks_map[task_id] = llm

    logging.info(f"New attack initiated with task_id: {task_id}")
    return jsonify({"status": "success", "req_id": task_id}), 200


@app.route('/generate_answer', methods=['POST'])
def generate_answer():
    logging.info("Received request to generate an answer.")
    global llm_tasks_queue

    task_id = request.json.get('task_id')
    prompt = request.json.get('prompt')

    llm_tasks_queue.put((task_id, prompt))
    logging.info(f"Task {task_id} added to LLM queue with prompt: {prompt}")
    return jsonify({"status": "success", "req_id": task_id}), 200


@app.route('/get_llm_result/<task_id>', methods=['GET'])
def get_llm_result(task_id):
    logging.info(f"Received request to get LLM result for task_id: {task_id}")
    global results, llm_tasks_map
    task_id = str(task_id)
    if task_id in results:
        answer = results.pop(task_id)
        if answer:
            logging.info(f"Answer retrieved for task_id: {task_id}")
            return jsonify({"status": "success", "answer": answer}), 200
        logging.error(f"Failed to retrieve answer for task_id: {task_id}")
        return jsonify({"status": "failed"}), 500
    logging.info(f"Task {task_id} is still pending.")
    return jsonify({"status": "pending"}), 202


if __name__ == "__main__":
    try:
        logging.info("Starting main server...")
        runner_thread = threading.Thread(target=runner_for_audio)
        llm_runner_thread = threading.Thread(target=runner_for_llm)
        runner_thread.start()
        llm_runner_thread.start()
        app.run(host='0.0.0.0', port=8080)
        stop.set()
    except Exception as e:
        stop.set()
        logging.error(f"Error occurred, shutting down... {e}")
