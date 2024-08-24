from flask import Flask, session
from flask_bootstrap import Bootstrap
import os
from dotenv import load_dotenv
from flask_login import LoginManager
from datetime import timedelta

from flask_socketio import SocketIO

from app.Server.data.fs import FilesManager
from app.Server.data.user import get_user_from_remote, User
from app.socketio_tasks import initialize_socketio

load_dotenv()


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
    attack_dir = "attack_records"
    attack_dir_path = os.path.join(project_dir, attack_dir)
    if not os.path.exists(attack_dir_path):
        os.makedirs(attack_dir_path)
    return attack_dir_path


login_manager = LoginManager()
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    user = User.get(int(user_id))
    return user


def create_app():
    app = Flask(
        __name__
    )  # The application as an object, Now can use this object to route and staff.

    app.config["SECRET_KEY"] = "hard to guess string"
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    audio_file_path = create_audio_file()
    video_file_path = create_video_file()

    app.config["UPLOAD_FOLDER"] = audio_file_path
    app.config["VIDEO_UPLOAD_FOLDER"] = video_file_path
    app.config["ATTACK_RECS"] = create_attack_file()

    socketio = SocketIO(app, async_mode=None)

    file_manager = FilesManager(audios_dir=audio_file_path, video_dir=video_file_path,
                                app_dir=os.path.dirname(os.path.realpath(__file__)))
    initialize_socketio(socketio, file_manager)  # function that initialized all the events for socketio with the app.

    bootstrap = Bootstrap(app)
    login_manager.init_app(app)

    # Register main blueprint
    from app.main import create_blueprint
    main_blueprint = create_blueprint(app, file_manager, socketio)
    app.register_blueprint(main_blueprint)

    # Register authentication blueprint
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # app.run(debug=True, use_reloader=True, host='0.0.0.0',
    #         threaded=True)  # Running the application.

    # Run the socketio instead of the app.
    socketio.run(app, debug=True, host='0.0.0.0',
                 use_reloader=True)
    return app, socketio
