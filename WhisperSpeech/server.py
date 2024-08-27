import os.path
import queue
import threading
import uuid

from flask import Flask, request, jsonify, send_file
import torchaudio
from whisperspeech.pipeline import Pipeline
from queue import Queue
from server_utils import *
from mfa import *

# Initialize Flask app
app = Flask(__name__)
tasks_queue = Queue()  # Q for the voice clone tasks
results = {}  # Dictionary to keep track the results
authorization_req = {}
default_file = os.path.join(os.path.dirname(__file__), '/speakers/Drake/Drake.mp3')  # File for healthcheck.
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
                if not os.path.exists(output_filename):
                    output_filename = generate_audio(text, speaker_wav_path, output_filename)

                if output_filename is not None:
                    results[task_id] = output_filename
                    print(f'task {task_id} done and saved in {output_filename}')
        except queue.Empty:
            continue


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


@app.route('/create_speaker_profile', methods=['POST'])
def create_profile():
    """
       Given a profile name and a wav file of the speaker, this route
       will save the new speaker with its wav audio file on the system.
    """
    data = request.get_json()
    speaker_wav = data.get('speaker_wav')
    profile_name = data.get('profile_name')

    if not speaker_wav or not profile_name:
        return jsonify({"error": "Missing required fields: text, speaker_wav, profile_name"}), 400

    profile_result_dir_path = os.path.join('speakers', profile_name)
    create_directory_if_not_exists(profile_result_dir_path)
    speaker_wav_path = os.path.join(profile_result_dir_path,
                                    f'{profile_name}_original_speech.wav')  # The existing wav file

    save_speaker_wav_to_dir(speaker_wav, speaker_wav_path)
    if os.path.exists(profile_result_dir_path) and os.path.exists(speaker_wav_path):
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400


@app.route('/generate_speech', methods=['POST'])
def generate_speech():
    global tasks_queue
    """
    Endpoint for generating speech from text and speaker wav.
    Given a profile name and text that the client want to clone using the 
    profile, this route will accept the request and pass it to the job Q.
    In addition, this route will return a task_id as a valid response to return the 
    result cloned voice from the '/get_result' endpoint.  
    """
    try:
        data = request.get_json()

        text = data.get('text')
        profile_name = data.get('profile_name')

        if not text or not profile_name:
            return jsonify({"error": "Missing required fields: text,profile_name"}), 400

        result_dir_path = os.path.join('speakers', profile_name)
        output_filename = os.path.join(result_dir_path, f'{clean_text(text)}.wav')  # The future cloned wav file
        speaker_wav_path = os.path.join(result_dir_path, f'{profile_name}_original_speech.wav')  # The existing wav file

        task_id = str(uuid.uuid4())  # Generate a unique task id, to future memorization what to return to whom.
        tasks_queue.put((task_id, (text, speaker_wav_path, output_filename)))
        return jsonify({"task_id": task_id}), 202

    except Exception as e:
        print(f"Error in /generate_speech: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/get_result/<task_id>', methods=['GET'])
def get_result(task_id):
    """
    Given a task_id, this route will return the cloned voice if it is done
    generating it, otherwise it will return a pending response inside the status.
     """
    global results
    if task_id in results:
        output_filename = results.pop(task_id)  # Get and rm the result.
        print(f"for task {task_id} speakers file is: {output_filename}")
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


@app.route('/authorize_user', methods=['POST'])
def authorize_login():
    """Sends a one-time code for 2fa."""
    email = request.json.get('email')
    otp_code = authenticate(email)
    if otp_code:
        send_email(email_receiver=email, email_subject="Your 2FA code", email_body=f"Your 2FA code is {otp_code}",
                   display_name="Deceptify Admin", from_email="DeceptifyAdmin<Do Not Replay>@gmail.com")
        req_id = uuid.uuid4()
        authorization_req[req_id] = otp_code
        return jsonify({"status": "success",
                        "req_id": req_id
                        }), 200
    return jsonify({"status": "failed"}), 500


@app.route('/validate_code', methods=['POST'])
def validate_code():
    global authorization_req

    req_id = request.json.get('req_id')
    code = request.json.get('code')

    if req_id in authorization_req:
        if code == authorization_req.pop(req_id):
            return jsonify({
                'authorize': True
            }), 200
        return jsonify({
            'authorize': False
        }), 200
    return jsonify({
        'status': "Cannot find your request."
    }), 500


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
