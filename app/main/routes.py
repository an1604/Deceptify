import base64
import os.path
import uuid
import os
import urllib
from flask import redirect as flask_redirect, jsonify, session, send_file
from app.Server.LLM.llm import llm

from flask import redirect as flask_redirect
from flask import jsonify, session, send_file, abort
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

from app.Server.Forms.general_forms import *
from app.Server.Forms.upload_data_forms import *
from app.Server.CamScript import RunVideo, ResetVirtualCam
from zoom_req import *
from app.Server.Forms.general_forms import *
from app.Server.Forms.upload_data_forms import *
from flask import render_template, url_for, flash, request, send_from_directory
from app.Server.Util import *
from app.Server.data.prompt import Prompt
from app.Server.data.Attacks import AttackFactory
from app.Server.data.Profile import Profile
from threading import Thread, Event
from dotenv import load_dotenv
from app.Server.speechToText import SRtest
from app.Server.speechToText import SRtest
from app.Server.CamScript import virtual_cam
import requests

load_dotenv()

CloseCallEvent = Event()
StopRecordEvent = Event()
CutVideoEvent = Event()
GetAnswerEvent = Event()

load_dotenv()
cam_thread = None
# Credentials For Zoom API
ZOOM_CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')
ZOOM_ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')
AUTH_URL = os.getenv('ZOOM_AUTH_URL')
REDIRECT_URI = os.getenv('REDIRECT_URI')
TOKEN_URL = os.getenv('TOKEN_URL')
BASE_ZOOM_URL = os.getenv('BASE_ZOOM_API_REQ_URL')


def error_routes(main):  # Error handlers routes
    @main.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @main.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500


def general_routes(main, app, data_storage):  # This function stores all the general routes.
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
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(data.filename))
            data.save(file_path)
            if video is not None:
                video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], secure_filename(video.filename))
                video.save(video_path)
                createvoice_profile(username="oded", profile_name=name, file_path=file_path)
                data_storage.add_profile(Profile(name, gen_info, str(file_path), video_data_path=str(video_path)))
            # else:
                # createvoice_profile(username="oded", profile_name=name, file_path=file_path)
                # data_storage.add_profile(Profile(name, gen_info, str(file_path)))
            if gen_info:
                response = llm.generate_knowledgebase(gen_info)
                rows = create_knowledgebase(response)
            # redirect to ollama
            flash("Profile created successfully")
            return flask_redirect(url_for("main.index"))
            # TODO: return flask_redirect(url_for('upload_voice_file')) FOR UPLOAD VOICE FILES FOR DATASET
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
        profile = data_storage.get_profile(request.args.get("profileo"))
        return render_template("profile.html", profileo=profile)

    @main.route("/transcript/<attack_id>")
    @login_required
    def transcript(attack_id):
        attack = data_storage.get_attack(attack_id)
        json_file_path = os.path.join(app.config['ATTACK_RECS'],
                                      f"Attacker-{attack.get_mimic_profile().getName()}-Target-{attack.getDesc()}.json")
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        return data

    @main.route("/recording/<attack_id>")
    @login_required
    def recording(attack_id):
        attack = data_storage.get_attack(attack_id)
        file_path = os.path.join(app.config['ATTACK_RECS'],
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
        encoded_start_url = request.args.get('start_url')
        start_url = urllib.parse.unquote(encoded_start_url) if encoded_start_url else None
        return render_template("dashboard.html", start_url=start_url)

    @main.route('/mp3/<path:filename>')  # Serve the MP3 files statically
    @login_required
    def serve_mp3(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @main.route('/video/<path:filename>')  # Serve the video files statically
    @login_required
    def serve_video(filename):
        return send_from_directory(app.config['VIDEO_UPLOAD_FOLDER'], filename)

    @main.route('/zoom_authorization')
    @login_required
    def zoom_authorization():
        auth_url = f'{AUTH_URL}?response_type=code&client_id={ZOOM_CLIENT_ID}&redirect_uri={REDIRECT_URI}'
        return flask_redirect(auth_url)

    @main.route('/zoom', methods=["GET", "POST"])
    @login_required
    def zoom():
        code = request.args.get('code')
        if code:
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI
            }
            credentials = f'{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}'
            encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.post(TOKEN_URL, data=data, headers=headers)
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
            print(access_token)
            if form.validate_on_submit():
                headers, data = generate_data_for_new_meeting(access_token=access_token,
                                                              meeting_name=form.meeting_name.data,
                                                              year=form.year.data, month=form.month.data,
                                                              day=form.day.data,
                                                              hour=form.hour.data, second=form.second.data,
                                                              minute=form.minute.data)

                start_url = create_new_meeting(headers=headers, data=data)
                print(start_url)
                encoded_start_url = urllib.parse.quote(start_url)
                return flask_redirect(url_for('main.dashboard', start_url=encoded_start_url))
            return render_template('generate_zoom_meeting.html', form=form)
        return abort(404)  # Aborting if we got no access token


def attack_generation_routes(main, app, data_storage):
    @main.route("/newattack", methods=["GET", "POST"])  # The new chat route.
    @login_required
    def newattack():
        form = CampaignForm()
        profNames = data_storage.getAllProfileNames()
        form.mimic_profile.choices = profNames
        form.target_profile.choices = profNames
        if form.validate_on_submit():
            campaign_name = form.campaign_name.data
            mimic_profile = data_storage.get_profile(form.mimic_profile.data)
            target_profile = data_storage.get_profile(form.target_profile.data)
            campaign_description = form.target_name.data
            attack_purpose = form.attack_purpose.data
            campaign_unique_id = int(uuid.uuid4())
            voice_type = form.voice_type.data
            place = form.place.data
            attack = AttackFactory.create_attack(
                "Voice",
                campaign_name,
                mimic_profile,
                target_profile,
                campaign_description,
                attack_purpose,
                campaign_unique_id,
                voice_type,
                place
            )
            data_storage.add_attack(attack)

            flash("Campaign created successfully using")
            return flask_redirect(
                url_for('main.attack_dashboard_transition', profile=form.mimic_profile.data,
                        contact=form.target_name.data, id=campaign_unique_id, type=voice_type))
        return render_template('attack_pages/newattack.html', form=form)

    @main.route('/attack_dashboard_transition', methods=['GET'])
    @login_required
    def attack_dashboard_transition():
        profile_name = request.args.get("profile")
        contact_name = request.args.get("contact")
        attack_id = request.args.get("id")
        if session.get("started_call"):
            session.pop("started_call")
        return render_template('attack_pages/attack_dashboard_transition.html', profile=profile_name,
                               contact=contact_name, id=attack_id)

    @main.route('/generate_attack_type', methods=['GET'])
    def generate_attack_type():
        profile_name = request.args.get('profile')
        attack_id = request.args.get('attack_id')
        profile = data_storage.get_profile(profile_name)
        attack = profile.get_attack(attack_id)
        attack_prompts = attack.get_attack_prompts()
        print(profile.getPrompts())
        for prompt in attack_prompts:
            if not profile.getPrompt(prompt):
                response = generate_voice("oded", profile.profile_name, prompt)
                get_voice_profile("oded", profile.profile_name, prompt, response["file"])
                new_prompt = Prompt(prompt_desc=prompt, prompt_profile=profile.profile_name)
                profile.addPrompt(new_prompt)
        print(attack.getPlace())
        starting_message = "Hello this is Jason from " + attack.getPlace()
        if starting_message not in attack_prompts:
            response = generate_voice("oded", profile.profile_name, starting_message)
            get_voice_profile("oded", profile.profile_name, starting_message, response["file"])
            new_prompt = Prompt(prompt_desc=starting_message, prompt_profile=profile.profile_name)
            profile.addPrompt(new_prompt)
        return jsonify({"status": "complete"})

    @main.route('/start_attack', methods=['GET', 'POST'])
    def start_attack():
        profile_name = request.args.get('profile')
        attack_id = request.args.get('attack_id')
        voice_type = request.args.get('voice_type')
        contact_name = request.args.get('contact')
        profile = data_storage.get_profile(profile_name)
        attack = profile.get_attack(attack_id)
        recorder_thread = Thread(target=record_call, args=(StopRecordEvent, "Attacker-" + profile_name +
                                                           "-Target-" + contact_name))
        recorder_thread.start()
        s2t_thread = Thread(target=SRtest.startConv, args=(app.config, profile_name, attack.getPurpose(),
                                                           "Hello this is jason from " + attack.getPlace(),
                                                           StopRecordEvent, contact_name))
        s2t_thread.start()
        return '', 204

    @main.route('/attack_dashboard', methods=['GET', 'POST'])
    @login_required
    def attack_dashboard():
        global cam_thread
        profile_name = request.args.get("profile")
        contact_name = request.args.get("contact")
        # attack_type = request.args.get("type")
        # attack_purpose = "Address"
        attack_id = request.args.get("id")
        profile = data_storage.get_profile(profile_name)
        attack = profile.get_attack(attack_id)
        attack_purpose = "address"
        form = AttackDashboardForm()
        form.prompt_field.choices = [(prompt.prompt_desc, prompt.prompt_desc) for prompt in profile.getPrompts()]

        started = session.get("started_call")
        if not started:
            recorder_thread = Thread(target=record_call, args=(StopRecordEvent, "Attacker-" + profile_name +
                                                               "-Target-" + contact_name))
            recorder_thread.start()
            session["started_call"] = True
            session['stopped_call'] = False
        if form.validate_on_submit():
            # if profile.video_data_path is not None and attack_type == "Video":
            #     CutVideoEvent.set()
            #     play_audio_thread = Thread(target=play_audio_through_vbcable,
            #                                args=(app.config['UPLOAD_FOLDER'] + "\\" + profile_name + "-" +
            #                                      form.prompt_field.data + ".wav", "CABLE Input"))
            #     play_audio_thread.start()
            #     cam_thread.join()
            #     cam_thread = Thread(target=RunVideo, args=(app.config['VIDEO_UPLOAD_FOLDER'] + "\\" + profile_name +
            #                                             "-" + form.prompt_field.data + ".mp4", False, CutVideoEvent))
            #     cam_thread.start()
            #     cam_thread.join()
            #     cam_thread = Thread(target=RunVideo, args=(app.config['VIDEO_UPLOAD_FOLDER'] + "\\" + profile_name +
            #                                                ".mp4", True, CutVideoEvent))
            #     cam_thread.start()
            #     play_audio_thread.join()
            #     return flask_redirect(url_for('main.attack_dashboard', profile=profile_name,
            #                                   contact=contact_name, type=attack_type))
            # else:
            play_audio_through_vbcable(os.path.join(app.config['UPLOAD_FOLDER'],
                                                    f"{profile_name}-{form.prompt_field.data}.wav"))
            return flask_redirect(url_for('main.attack_dashboard', profile=profile_name,
                                            contact=contact_name, id=attack_id))
        return render_template('attack_pages/attack_dashboard.html', form=form,
                               contact=contact_name, id=attack_id)

    @main.route('/send_prompt', methods=['GET'])
    @login_required
    def send_prompt():
        prompt_path = request.args.get("prompt_path")
        return play_audio_through_vbcable(prompt_path)

    @main.route("/information_gathering", methods=["GET", "POST"])
    @login_required
    def information_gathering():
        return flask_redirect(url_for("main.newattack"))

    @main.route("/collect_video", methods=["GET", "POST"])
    @login_required
    def collect_video():
        form = VideoUploadForm()
        if form.validate_on_submit():
            video = form.video_field.data
            return flask_redirect(url_for("main.newattack"))
        return render_template("data_collection_pages/collect_video.html", form=form)

    @main.route("/collect_dataset", methods=["GET", "POST"])
    @login_required
    def collect_dataset():
        form = DataSetUploadForm()
        if form.validate_on_submit():
            dataset = form.file_field.data
            return flask_redirect(url_for("main.newattack"))
        return render_template("data_collection_pages/collect_dataset.html", form=form)

    @main.route("/new_voice_attack", methods=["GET", "POST"])  # New voice attack page.
    @login_required
    def new_voice_attack():
        form = VoiceChoiceForm()
        if form.validate_on_submit():
            choice = form.selection.data
            if "upload" in choice.lower():
                return flask_redirect(url_for("main.upload_voice_file"))
            else:
                return flask_redirect(url_for("main.record_voice"))
        return render_template("attack_pages/new_voice_attack.html", form=form)

    @main.route("/upload_voice_file", methods=["GET", "POST"])
    @login_required
    def upload_voice_file():
        form = VoiceUploadForm()
        if form.validate_on_submit():
            wavs_filepath, profile_directory = create_wavs_directory_for_dataset(app.config['UPLOAD_FOLDER'])
            for file in form.files.data:
                filename = secure_filename(file.filename)
                file_path = os.path.join(wavs_filepath, filename)
                file.save(file_path)
            create_csv(wavs_filepath, profile_directory)
            return flask_redirect(url_for("main.newattack"))
        return render_template("data_collection_pages/upload_voice_file.html", form=form)

    @main.route(
        "/record_voice", methods=["GET", "POST"]
    )  # Route for record a new voice file.
    @login_required
    def record_voice():
        return render_template("data_collection_pages/record_voice.html")

    @main.route("/save-record", methods=["GET", "POST"])
    @login_required
    def save_record():
        if "file" not in request.files:
            flash("No file part")
            return flask_redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return flask_redirect(request.url)
        file_name = str(uuid.uuid4()) + ".mp3"
        full_file_name = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
        file.save(full_file_name)
        return "<h1>File saved</h1>"

    @main.route("/view_audio_prompts", methods=["GET", "POST"])
    @login_required
    def view_audio_prompts():
        prof = data_storage.get_profile(request.args.get("profile"))
        Addform = PromptAddForm(profile=prof)
        Deleteform = PromptDeleteForm(profile=prof)
        Deleteform.prompt_delete_field.choices = [(prompt.prompt_desc, prompt.prompt_desc) for prompt in
                                                  prof.getPrompts()]
        if Addform.submit_add.data and Addform.validate_on_submit():
            desc = Addform.prompt_add_field.data
            response = generate_voice("oded", prof.profile_name, desc)
            get_voice_profile("oded", prof.profile_name, desc, response["file"])
            new_prompt = Prompt(prompt_desc=desc, prompt_profile=prof.profile_name)
            prof.addPrompt(new_prompt)
            return flask_redirect(url_for('main.view_audio_prompts', profile=prof.profile_name))
        if Deleteform.submit_delete.data and Deleteform.validate_on_submit():
            desc = Deleteform.prompt_delete_field.data
            prof.deletePrompt(desc)
            return flask_redirect(url_for('main.view_audio_prompts', profile=prof.profile_name))
        return render_template('attack_pages/view_audio_prompts.html', Addform=Addform, Deleteform=Deleteform,
                               prompts=prof.getPrompts())

    @main.route("/view_video_prompts", methods=["GET", "POST"])
    @login_required
    def view_video_prompts():
        prof = data_storage.get_profile(request.args.get("profile"))
        Addform = PromptAddForm(profile=prof)
        Deleteform = PromptDeleteForm(profile=prof)
        video_prompts = set()
        for prompt in prof.getPrompts():
            if prompt.is_video:
                video_prompts.add(prompt)
        Deleteform.prompt_delete_field.choices = [(prompt.prompt_desc, prompt.prompt_desc) for prompt in video_prompts]
        if Addform.submit_add.data and Addform.validate_on_submit():
            desc = Addform.prompt_add_field.data
            new_prompt = Prompt(prompt_desc=desc, prompt_profile=prof.profile_name, is_video=True)
            prof.addPrompt(new_prompt)
            return flask_redirect(url_for('main.view_video_prompts', profile=prof.profile_name))
        if Deleteform.submit_delete.data and Deleteform.validate_on_submit():
            desc = Deleteform.prompt_delete_field.data
            prof.deletePrompt(desc)
            return flask_redirect(url_for('main.view_video_prompts', profile=prof.profile_name))
        return render_template('attack_pages/view_video_prompts.html', Addform=Addform, Deleteform=Deleteform,
                               prompts=video_prompts)

    @main.route("/end_call", methods=["GET", "POST"])
    @login_required
    def end_call():
        session['stopped_call'] = True
        CloseCallEvent.set()
        StopRecordEvent.set()
        CutVideoEvent.set()
        ResetVirtualCam()
        session.pop("started_call", None)
        return jsonify({})


def execute_routes(main, app, data_storage):  # Function that executes all the routes.
    general_routes(main, app, data_storage)  # General pages navigation
    attack_generation_routes(main, app, data_storage)  # Attack generation pages navigation
    error_routes(main)  # Errors pages navigation



