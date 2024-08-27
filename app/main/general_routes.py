import base64
import urllib

from flask import redirect as flask_redirect, jsonify, session, send_file, abort, render_template, url_for, flash, \
    request, send_from_directory
from werkzeug.utils import secure_filename
from flask_login import login_required

from zoom_req import *
from app.Server.Forms.general_forms import *
from app.Server.Util import *
from app.Server.data.Profile import Profile
from app.main.main_params import MainRotesParams


def general_routes(main, data_storage, file_manager, socketio):  # This function stores all the general routes.
    @main.route("/", methods=["GET", "POST"])  # The root router (welcome page).
    def index():
        return render_template("index.html")

    @main.route('/save_exit')
    @login_required
    def save_exit():
        # Save the data
        data_storage.save_data()
        session['message'] = 'Session saved!'
        return index()

    @main.route("/new_profile", methods=["GET", "POST"])
    @login_required
    def new_profile():
        form = ProfileForm()
        if form.validate_on_submit():
            # Get the data from the form
            name = form.name_field.data
            gen_info = form.gen_info_field.data
            data = form.recording_upload.data
            video = form.Image_upload.data
            if video.filename == "":
                video = None

            # Save the voice sample
            speaker_wavfile_path = file_manager.get_file_from_audio_dir(secure_filename(data.filename))
            data.save(speaker_wavfile_path)
            if create_voice_profile(username="oded", profile_name=name,
                                    speaker_wavfile_path=speaker_wavfile_path):
                data_storage.add_profile(Profile(name, gen_info, str(speaker_wavfile_path)))

            flash("Profile created successfully")
            return flask_redirect(url_for("main.index"))
        return render_template("attack_pages/new_profile.html", form=form)

    @main.route("/profileview", methods=["GET", "POST"])
    @login_required
    def profileview():
        form = ViewProfilesForm()
        tmp = data_storage.getAllProfileNames()
        form.profile_list.choices = tmp
        if form.validate_on_submit():
            if form.profile_list.data == "No profiles available, time to create some!":
                flash("No profiles available, time to create some!")
                return flask_redirect(url_for("main.new_profile"))
            return flask_redirect(url_for("main.profile", profileo=form.profile_list.data))
        return render_template("profileview.html", form=form)

    @main.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        profile = data_storage.get_profile(request.args.get("profile"))
        return render_template("profile.html", profileo=profile)

    @main.route("/transcript/<attack_id>")
    @login_required
    def transcript(attack_id):
        attack = data_storage.get_attack(attack_id)
        json_file_path = file_manager.get_file_from_attack_dir(
            f"Attacker-{attack.get_mimic_profile().getName()}-Target-{attack.getDesc()}.json")
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        return data

    @main.route("/recording/<attack_id>")
    @login_required
    def recording(attack_id):
        attack = data_storage.get_attack(attack_id)
        file_path = file_manager.get_file_from_attack_dir(
            f"Attacker-{attack.get_mimic_profile().getName()}-Target-{attack.getID()}.wav")
        return send_file(file_path)

    @main.route("/contact", methods=["GET", "POST"])
    def contact():
        form = ContactForm()
        if form.validate_on_submit():
            email = form.email.data
            contact_field = form.contact_field.data
            passwd = form.passwd.data
            return flask_redirect(url_for("main.index"))
        return render_template("contact.html", form=form)

    @main.route("/dashboard", methods=["GET", "POST"])
    @login_required
    def dashboard():
        attacks = data_storage.get_ai_attacks()
        return render_template("dashboard.html", attacks=attacks)

    @main.route('/mp3/<path:filename>')  # Serve the MP3 files statically
    @login_required
    def serve_mp3(filename):
        return send_from_directory(file_manager.audios_dir, filename)

    @main.route('/download_file/<filename>')
    @login_required
    def download_file(filename):
        print(filename)
        return send_file(file_manager.get_file_from_attack_dir(filename))

    @main.route('/video/<path:filename>')  # Serve the video files statically
    @login_required
    def serve_video(filename):
        return send_from_directory(filename.video_dir, filename)

    @main.route('/get_audio')
    def get_audio():
        file_path = request.args.get('file_path')
        if file_path:
            return send_file(file_path, mimetype='audio/mpeg')
        return "Audio file not found", 404

    @main.route('/telegram_info')
    @login_required
    def telegram_info():
        return render_template('telegram/telegram_info.html')

    @main.route('/run_telegram_attack', methods=['GET', 'POST'])
    @login_required
    def run_telegram_attack():
        # profile_name = request.args.get('profile_name')
        return render_template('telegram/run_telegram_attack.html')

    @main.route('/zoom_authorization')
    @login_required
    def zoom_authorization():
        session['whatsapp_attack_info'] = {
            'attack_id': request.args.get('id'),
            'zoom_url': None
        }
        auth_url = f'{MainRotesParams.AUTH_URL}?response_type=code&client_id={MainRotesParams.ZOOM_CLIENT_ID}&redirect_uri={MainRotesParams.REDIRECT_URI}'
        return flask_redirect(auth_url)

    @main.route('/zoom', methods=["GET", "POST"])
    @login_required
    def zoom():
        code = request.args.get('code')
        if code:
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': MainRotesParams.REDIRECT_URI
            }
            credentials = f'{MainRotesParams.ZOOM_CLIENT_ID}:{MainRotesParams.ZOOM_CLIENT_SECRET}'
            encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.post(MainRotesParams.TOKEN_URL, data=data, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                refresh_token = response_data.get('refresh_token')
                access_token = response_data.get('access_token')

                session['zoom_access_credentials'] = {
                    'refresh_token': refresh_token,
                    'access_token': access_token
                }
                return flask_redirect(url_for('main.generate_zoom_record'))
            else:
                return jsonify({'error': 'Failed to retrieve tokens'}), response.status_code
        else:
            return jsonify({'error': 'No code parameter provided'}), 400

    @main.route('/generate_zoom_record', methods=["GET", "POST"])
    @login_required
    def generate_zoom_record():
        form = ZoomMeetingForm()
        if 'zoom_access_credentials' in session:
            access_token = session['zoom_access_credentials'].get('access_token')
            if form.validate_on_submit():
                headers, data = generate_data_for_new_meeting(access_token=access_token,
                                                              meeting_name=form.meeting_name.data,
                                                              year=form.year.data, month=form.month.data,
                                                              day=form.day.data,
                                                              hour=form.hour.data, second=form.second.data,
                                                              minute=form.minute.data)

                start_url = create_new_meeting(headers=headers, data=data)
                encoded_start_url=urllib.parse.quote(start_url)
                return flask_redirect(url_for('main.attack_dashboard_transition', start_url=encoded_start_url))
            return render_template('generate_zoom_meeting.html', form=form)
        return abort(404)  # Aborting if we got no access token
