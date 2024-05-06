import time
import uuid

from flask import Flask, render_template, make_response, session, url_for, flash, request
from flask_bootstrap import Bootstrap
import os
from dotenv import load_dotenv

from flask import redirect as flask_redirect
from werkzeug.utils import secure_filename

from forms import *

load_dotenv()


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


    bootstrap = Bootstrap(app)

    @app.route('/', methods=['GET', 'POST'])  # The root router (welcome page).
    def index():
        return render_template('index.html')

    @app.route('/newchat', methods=['GET', 'POST'])  # The new chat route.
    def newchat():
        return render_template('newchat.html')

    @app.route('/new_voice_attack', methods=['GET', 'POST'])  # New voice attack page.
    def new_voice_attack():
        passwd = None
        form = VoiceChoiceForm()
        if form.validate_on_submit():
            passwd = form.passwd.data
            choice = form.selection.data
            if 'upload' in choice.lower():
                return flask_redirect(url_for('upload_voice_file'))
            else:
                return flask_redirect(url_for('record_voice'))
        return render_template('new_voice_attack.html', form=form)

    @app.route('/upload_voice_file', methods=['GET', 'POST'])  # Route for uploading an existing voice rec file.
    def upload_voice_file():
        voice_file = None
        passwd = None
        form = VoiceUploadForm()
        if form.validate_on_submit():
            voice_file = form.file_field.data
            passwd = form.passwd.data
            if voice_file.filename == '':
                flash('No selected file')
                return flask_redirect(request.url)
            # file_name = str(voice_file) + ".mp3"
            file_name = secure_filename(voice_file.filename)
            full_file_name = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
            voice_file.save(full_file_name)
            flash('Voice uploaded to the server!')
            return flask_redirect(url_for('new_voice_attack'))
        return render_template('upload_voice_file.html', form=form)

    @app.route('/record_voice', methods=['GET', 'POST'])  # Route for record a new voice file.
    def record_voice():
        return render_template('record_voice.html')

    @app.route('/save-record', methods=['GET', 'POST'])
    def save_record():
        # check if the post-request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return flask_redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return flask_redirect(request.url)
        file_name = str(uuid.uuid4()) + ".mp3"
        full_file_name = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(full_file_name)
        return '<h1>File saved</h1>'

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        email = None
        contact_field = None
        passwd = None
        form = ContactForm()
        if form.validate_on_submit():
            email = form.email.data
            contact_field = form.contact_field.data
            passwd = form.passwd.data
            return flask_redirect(url_for('index'))
        return render_template('contact.html', form=form)

    @app.route('/dashboard', methods=['GET', 'POST'])
    def dashboard():
        return render_template('dashboard.html')

    # Error handlers routes
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    return app
