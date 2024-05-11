import time
import uuid
import queue

import requests
from flask import Flask, render_template, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from Server.routes import execute_routes

load_dotenv()

remote_server_ip = os.getenv("REMOTE_SERVER_IP")
remote_server_port = os.getenv("REMOTE_SERVER_PORT")
updates_queue = queue.Queue()  # Queue for handling updates from the remote server.
data = None  # The data parameter keeps the last update from the remoter server.
db = None


def check_for_updates():  # This function will run in the background to communicate with the remote server.
    global updates_queue, data
    print("Checking for updates (in the background)...")
    while True:
        try:
            time.sleep(10)  # Waits 10 seconds before each request.
            url = f"http://{remote_server_ip}:{remote_server_port}/updates"  # TODO: CHANGE THE URL ACCORDING TO OUT NEEDS.
            headers = {  # TODO: ADJUST THE HEADERS.
                'Content-Type': 'application/json',
                'Secret_key': os.getenv("SECRET_KEY"),
                'User_id': os.getenv("USER_ID"),
            }
            response = requests.post(url, headers=headers)
            if response.status_code == 200:
                data = response.json()  # Updating the data parameter.
                updates_queue.put(data)  # Put in the Q also.
        except Exception as e:
            print(e)


def create_audio_file():
    project_dir = os.path.dirname(os.path.realpath(__file__))
    audio_dir = "AudioFiles"
    audio_dir_path = os.path.join(project_dir, audio_dir)
    if not os.path.exists(audio_dir_path):
        os.makedirs(audio_dir_path)
    return audio_dir_path


def create_app():
    app = Flask(__name__)  # The application as an object, Now can use this object to route and staff.

    # app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # A secret key for the encryption process (not really useful).
    app.config['SECRET_KEY'] = 'hard to guess string'

    audio_file_path = create_audio_file()
    app.config['UPLOAD_FOLDER'] = audio_file_path
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # The database URI.
    bootstrap = Bootstrap(app)
    global db
    db = SQLAlchemy(app)
    execute_routes(app)  # Executing the routes

    # TODO: UNCOMMENT THIS ROWS!
    #  THIS IS THE BACKGROUND THREAD FOR UPDATES CHECKING!!!!
    # Set up a background thread for updates and other staff to get from the remoter server.
    # updates_checker = threading.Thread(target=check_for_updates)
    # updates_checker.daemon = True
    # updates_checker.start()

    app.run(debug=True, use_reloader=False)  # Running the application.
    return app
