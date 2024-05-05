from flask import Flask, render_template, make_response, session, url_for, flash
from flask_bootstrap import Bootstrap
import os
from dotenv import load_dotenv

from flask import redirect as flask_redirect

from UtilFuns import *
from forms import *

load_dotenv()

SECRET_KEY = 'hard to guess key'
def create_app():
    app = Flask(__name__)  # The application as an object, Now can use this object to route and staff.
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # A secret key for the encryption process (not really useful).
    bootstrap = Bootstrap(app)

    @app.route('/', methods=['GET', 'POST'])  # The root router (welcome page).
    def index():
        return render_template('templates/index.html')

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
            flash('Voice uploaded to the server!')
            return flask_redirect(url_for('new_voice_attack'))
        return render_template('upload_voice_file.html', form=form)

    @app.route('/record_voice', methods=['GET', 'POST'])  # Route for record a new voice file.
    def record_voice():
        press_to_record = NewVoiceRecord()
        if press_to_record.validate_on_submit():
            session['IS_RECORD'] = True
            print("Before function called")
            # Omer 5/5/24 temporary ugly logic till i make new method for self recording
            inouttuple = grabAudioIO()
            record = recordConvo(inouttuple[0], inouttuple[1])  # Records the client's voice for maximum 10 seconds.
            print("After function called")
            flash('Please Record your message.')
            return flask_redirect(url_for('new_voice_attack'))
        return render_template('record_voice.html', form=press_to_record)

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

    @app.errorhandler(Exception)
    def exception_handler(error):
        return render_template('404.html'), 404

    return app

# if __name__ == '__main__':
#     app.run(debug=True)  # TODO: Remove the debug=True in production.
