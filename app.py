import time
import queue
import requests
from flask import Flask
from flask_bootstrap import Bootstrap
import os
from dotenv import load_dotenv
from routes import execute_routes
from Server.data.DataStorage import DataStorage

load_dotenv()

remote_server_ip = os.getenv("REMOTE_SERVER_IP")
remote_server_port = os.getenv("REMOTE_SERVER_PORT")
updates_queue = queue.Queue()  # Queue for handling updates from the remote server.
data = None  # The data parameter keeps the last update from the remoter server.


def create_audio_file():
    project_dir = os.path.dirname(os.path.realpath(__file__))
    audio_dir = "Server/AudioFiles"
    audio_dir_path = os.path.join(project_dir, audio_dir)
    if not os.path.exists(audio_dir_path):
        os.makedirs(audio_dir_path)
    return audio_dir_path


def create_video_file():
    project_dir = os.path.dirname(os.path.realpath(__file__))
    video_dir = "Server/VideoFiles"
    video_dir_path = os.path.join(project_dir, video_dir)
    if not os.path.exists(video_dir_path):
        os.makedirs(video_dir_path)
    return video_dir_path


def create_attack_file():
    project_dir = os.path.dirname(os.path.realpath(__file__))
    attack_dir = "Server/attack_records"
    attack_dir_path = os.path.join(project_dir, attack_dir)
    if not os.path.exists(attack_dir_path):
        os.makedirs(attack_dir_path)
    return attack_dir_path


def create_app():
    app = Flask(
        __name__
    )  # The application as an object, Now can use this object to route and staff.

    # app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # A secret key for the encryption process (not really useful).
    app.config["SECRET_KEY"] = "hard to guess string"

    audio_file_path = create_audio_file()
    video_file_path = create_video_file()
    app.config["UPLOAD_FOLDER"] = audio_file_path
    app.config["VIDEO_UPLOAD_FOLDER"] = video_file_path
    app.config["ATTACK_RECS"] = create_attack_file()
    bootstrap = Bootstrap(app)

    data_storage = DataStorage().load_data()
    execute_routes(app, data_storage)  # Executing the routes
    app.run(debug=True, use_reloader=True)  # Running the application.
    return app


if __name__ == "__main__":
    create_app()
