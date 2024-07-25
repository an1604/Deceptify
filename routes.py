import uuid

from flask import redirect as flask_redirect, jsonify, session, send_file
from werkzeug.utils import secure_filename

from Server.Forms.general_forms import *
from Server.Forms.upload_data_forms import *
from flask import render_template, url_for, flash, request, send_from_directory
from Server.Util import *
from Server.data.prompt import Prompt
from Server.data.Attacks import AttackFactory
from Server.data.Profile import Profile
from threading import Thread, Event
from dotenv import load_dotenv
from Server.speechToText import SRtest

CloseCallEvent = Event()
StopRecordEvent = Event()
GetAnswerEvent = Event()

load_dotenv()

SERVER_URL = os.getenv('SERVER_URL')


def error_routes(app):  # Error handlers routes
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500


def general_routes(app, data_storage):  # This function stores all the general routes.
    @app.route("/", methods=["GET", "POST"])  # The root router (welcome page).
    def index():
        return render_template("index.html")

    @app.route('/save_exit')
    def save_exit():
        # Save the data
        data_storage.save_data()

        # Shutdown the server
        # TODO: Fix the server shutdown tmp redirect to index for now
        # shutdown_function = request.environ.get('werkzeug.server.shutdown')
        # if shutdown_function is None:
        #     raise RuntimeError('Not running with the Werkzeug Server')
        # shutdown_function()
        # return 'Server shutting down...'
        session['message'] = 'Session saved!'
        return index()

    @app.route("/new_profile", methods=["GET", "POST"])
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
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], data.filename)
            data.save(file_path)
            if video is not None:
                video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], video.filename)
                video.save(video_path)
                data_storage.add_profile(Profile(name, gen_info, str(file_path), video_data_path=str(video_path)))

            else:
                # Pass the profile info and voice sample to server
                createvoice_profile(username="oded", profile_name=name, file_path=file_path)
                data_storage.add_profile(Profile(name, gen_info, str(file_path)))

            flash("Profile created successfully")
            return flask_redirect(url_for("index"))
        return render_template("attack_pages/new_profile.html", form=form)

    @app.route("/profileview", methods=["GET", "POST"])
    def profileview():
        form = ViewProfilesForm()
        print("HELLO")
        # tmp = [(profile.getName(), profile.getName()) for profile in data_storage.get_profiles()]
        tmp = data_storage.getAllProfileNames()
        form.profile_list.choices = tmp
        if form.validate_on_submit():
            if form.profile_list.data == "No profiles available, time to create some!":
                flash("No profiles available, time to create some!")
                return flask_redirect(url_for("new_profile"))
            return flask_redirect(url_for("profile", profileo=form.profile_list.data))
        return render_template("profileview.html", form=form)

    @app.route("/profile", methods=["GET", "POST"])
    def profile():
        profile = data_storage.get_profile(request.args.get("profileo"))
        return render_template("profile.html", profileo=profile)

    @app.route("/transcript/<attack_id>")
    def transcript(attack_id):
        attack = data_storage.get_attack(attack_id)
        json_file_path = (app.config['ATTACK_RECS'] + "\\" + "Attacker-" + attack.get_mimic_profile().getName()
                          + "-Target-" + attack.getDesc() + ".json")
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            print(data)
        return data

    @app.route("/recording/<attack_id>")
    def recording(attack_id):
        attack = data_storage.get_attack(attack_id)
        print(attack.get_target())
        file_path = (app.config['ATTACK_RECS'] + "\\" + "Attacker-" + attack.get_mimic_profile().getName() + "-Target-"
                     + attack.getID() + ".wav")
        return send_file(file_path)

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        email = None
        contact_field = None
        passwd = None
        form = ContactForm()
        if form.validate_on_submit():
            email = form.email.data
            contact_field = form.contact_field.data
            passwd = form.passwd.data
            return flask_redirect(url_for("index"))
        return render_template("contact.html", form=form)

    @app.route("/dashboard", methods=["GET", "POST"])
    def dashboard():
        return render_template("dashboard.html")

    @app.route('/mp3/<path:filename>')  # Serve the MP3 files statically
    def serve_mp3(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/video/<path:filename>')  # Serve the video files statically
    def serve_video(filename):
        return send_from_directory(app.config['VIDEO_UPLOAD_FOLDER'], filename)


def attack_generation_routes(app, data_storage):
    @app.route("/newattack", methods=["GET", "POST"])  # The new chat route.
    def newattack():
        # omer 11/5/24 added form and capturing data + generating unique id
        form = CampaignForm()
        profNames = data_storage.getAllProfileNames()
        form.mimic_profile.choices = profNames
        form.target_profile.choices = profNames
        if form.validate_on_submit():
            campaign_name = form.campaign_name.data
            mimic_profile = data_storage.get_profile(form.mimic_profile.data)
            target_profile = data_storage.get_profile(form.target_profile.data)
            campaign_description = form.target_name.data
            attack_type = form.attack_type.data
            attack_purpose = form.attack_purpose.data
            campaign_unique_id = int(uuid.uuid4())
            attack = AttackFactory.create_attack(
                attack_type,
                campaign_name,
                mimic_profile,
                target_profile,
                campaign_description,
                attack_purpose,
                campaign_unique_id,
            )
            data_storage.add_attack(attack)

            flash("Campaign created successfully using")
            return flask_redirect(url_for('attack_dashboard_transition', profile=form.mimic_profile.data,
                                          contact=form.target_name.data))
        return render_template('attack_pages/newattack.html', form=form)

    @app.route('/attack_dashboard_transition', methods=['GET'])
    def attack_dashboard_transition():
        profile_name = request.args.get("profile")
        contact_name = request.args.get("contact")
        return render_template('attack_pages/attack_dashboard_transition.html', profile=profile_name,
                               contact=contact_name)

    @app.route('/attack_dashboard', methods=['GET', 'POST'])
    def attack_dashboard():

        profile_name = request.args.get("profile")
        contact_name = request.args.get("contact")
        profile = data_storage.get_profile(profile_name)
        form = AttackDashboardForm()
        form.prompt_field.choices = [(prompt.prompt_desc, prompt.prompt_desc)
                                     for prompt in profile.getPrompts()]

        started = session.get("started_call")
        if not started:
            # TODO: make video attack in case of video profile. the function will provide default video with obs
            # if profile.video_data_path is not None:

            s2t_thread = Thread(target=SRtest.startConv, args=(app.config, profile_name))
            s2t_thread.start()
            # thread_call = Thread(target=ExecuteCall, args=(contact_name, CloseCallEvent))
            # thread_call.start()
            recorder_thread = Thread(target=record_call, args=(StopRecordEvent, "Attacker-" + profile_name +
                                                               "-Target-" + contact_name))
            s2t_thread.join()
            StopRecordEvent.set()

            # # Omer's call recording NEED TO BE TESTED ON WINDOWS
            #
            # recorder = CallRecorder()
            # recording_thread = Thread(target=recorder.start_recording)
            # recording_thread.start()
            # # When you want to stop recording, call:
            # # recorder.stop_recording()

            # Create a new thread for the speech to text
            # s2t = SpeechToText((Util.dateTimeName('_'.join([profile_name, contact_name, "voice_call"]))))
            # s2t.start()

            session["started_call"] = True
            session['stopped_call'] = False
        if form.validate_on_submit():
            if profile.video_data_path is not None:
                # TODO: add the video attack function using obs. this will change video to custom video and return it
                #  back to the default video after
                return flask_redirect(url_for('attack_dashboard', profile=profile_name, contact=contact_name))
            else:
                play_audio_through_vbcable(app.config['UPLOAD_FOLDER'] + "\\" + profile_name + "-" +
                                           form.prompt_field.data + ".wav")
                return flask_redirect(url_for('attack_dashboard', profile=profile_name, contact=contact_name))
        return render_template('attack_pages/attack_dashboard.html', form=form, contact=contact_name)

    @app.route('/send_prompt', methods=['GET'])
    def send_prompt():
        prompt_path = request.args.get("prompt_path")
        return play_audio_through_vbcable(prompt_path)

    @app.route("/information_gathering", methods=["GET", "POST"])
    def information_gathering():
        return flask_redirect(url_for("newattack"))
        # form = InformationGatheringForm()
        # if form.validate_on_submit():
        #     choice = form.selection.data.lower()
        #     if "datasets" in choice:
        #         return flask_redirect(url_for("collect_dataset"))
        #     elif "recordings" in choice:
        #         return flask_redirect(url_for("new_voice_attack"))
        #     elif "video" in choice:
        #         return flask_redirect(url_for("collect_video"))
        # return render_template(
        #     "data_collection_pages/information_gathering.html", form=form
        # )

    @app.route("/collect_video", methods=["GET", "POST"])
    def collect_video():
        form = VideoUploadForm()
        if form.validate_on_submit():
            video = form.video_field.data
            return flask_redirect(url_for("newattack"))
        return render_template("data_collection_pages/collect_video.html", form=form)

    @app.route("/collect_dataset", methods=["GET", "POST"])
    def collect_dataset():
        form = DataSetUploadForm()
        if form.validate_on_submit():
            dataset = form.file_field.data
            return flask_redirect(url_for("newattack"))
        return render_template("data_collection_pages/collect_dataset.html", form=form)

    @app.route("/new_voice_attack", methods=["GET", "POST"])  # New voice attack page.
    def new_voice_attack():
        passwd = None
        form = VoiceChoiceForm()
        if form.validate_on_submit():
            passwd = form.passwd.data
            choice = form.selection.data
            if "upload" in choice.lower():
                return flask_redirect(url_for("upload_voice_file"))
            else:
                return flask_redirect(url_for("record_voice"))
        return render_template("attack_pages/new_voice_attack.html", form=form)

    @app.route(
        "/upload_voice_file", methods=["GET", "POST"]
    )  # Route for uploading an existing voice rec file.
    def upload_voice_file():
        voice_file = None
        passwd = None
        form = VoiceUploadForm()
        if form.validate_on_submit():
            voice_file = form.file_field.data
            passwd = form.passwd.data
            if voice_file.filename == "":
                flash("No selected file")
                return flask_redirect(request.url)
            file_name = secure_filename(voice_file.filename)
            full_file_name = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
            voice_file.save(full_file_name)
            flash("Voice uploaded to the server!")
            return flask_redirect(url_for("newattack"))
        return render_template(
            "data_collection_pages/upload_voice_file.html", form=form
        )

    @app.route(
        "/record_voice", methods=["GET", "POST"]
    )  # Route for record a new voice file.
    def record_voice():
        return render_template("data_collection_pages/record_voice.html")

    @app.route("/save-record", methods=["GET", "POST"])
    def save_record():
        # check if the post-request has the file part
        if "file" not in request.files:
            flash("No file part")
            return flask_redirect(request.url)
        file = request.files["file"]
        # if a user does not select file, the browser also
        # submits an empty part without a filename
        if file.filename == "":
            flash("No selected file")
            return flask_redirect(request.url)
        file_name = str(uuid.uuid4()) + ".mp3"
        full_file_name = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
        file.save(full_file_name)
        return "<h1>File saved</h1>"

    @app.route("/view_audio_prompts", methods=["GET", "POST"])
    def view_audio_prompts():
        prof = data_storage.get_profile(request.args.get("profile"))
        Addform = PromptAddForm(profile=prof)
        Deleteform = PromptDeleteForm(profile=prof)
        Deleteform.prompt_delete_field.choices = [(prompt.prompt_desc, prompt.prompt_desc)
                                                  for prompt in prof.getPrompts()]
        if Addform.submit_add.data and Addform.validate_on_submit():
            desc = Addform.prompt_add_field.data
            response = generate_voice("oded", prof.profile_name, desc)
            get_voice_profile("oded", prof.profile_name, desc, response["file"])
            new_prompt = Prompt(prompt_desc=desc, prompt_profile=prof.profile_name)
            prof.addPrompt(new_prompt)
            return flask_redirect(url_for('view_audio_prompts', profile=prof.profile_name))
        if Deleteform.submit_delete.data and Deleteform.validate_on_submit():
            desc = Deleteform.prompt_delete_field.data
            prof.deletePrompt(desc)
            return flask_redirect(url_for('view_audio_prompts', profile=prof.profile_name))
        return render_template('attack_pages/view_audio_prompts.html', Addform=Addform,
                               Deleteform=Deleteform, prompts=prof.getPrompts())

    @app.route("/view_video_prompts", methods=["GET", "POST"])
    def view_video_prompts():
        prof = data_storage.get_profile(request.args.get("profile"))
        Addform = PromptAddForm(profile=prof)
        Deleteform = PromptDeleteForm(profile=prof)
        video_prompts = set()
        for prompt in prof.getPrompts():
            if prompt.is_video:
                video_prompts.add(prompt)
        Deleteform.prompt_delete_field.choices = [(prompt.prompt_desc, prompt.prompt_desc)
                                                  for prompt in video_prompts]
        # TODO: fix the problem where a video prompt cant be added because there exists a voice prompt
        if Addform.submit_add.data and Addform.validate_on_submit():
            desc = Addform.prompt_add_field.data
            # TODO: replace voice with video generation
            # response = Util.generate_voice("oded", prof.profile_name, desc)
            # Util.get_voice_profile("oded", prof.profile_name, desc, response["file"])

            new_prompt = Prompt(prompt_desc=desc, prompt_profile=prof.profile_name, is_video=True)
            prof.addPrompt(new_prompt)
            return flask_redirect(url_for('view_video_prompts', profile=prof.profile_name))

        # TODO: fix problem where a prompt is deleted on audio and video when deleting video
        if Deleteform.submit_delete.data and Deleteform.validate_on_submit():
            desc = Deleteform.prompt_delete_field.data
            prof.deletePrompt(desc)
            return flask_redirect(url_for('view_video_prompts', profile=prof.profile_name))
        return render_template('attack_pages/view_video_prompts.html', Addform=Addform,
                               Deleteform=Deleteform, prompts=video_prompts)

    @app.route("/end_call", methods=["GET", "POST"])
    def end_call():
        print("close_window")
        session['stopped_call'] = True  # Set the flag to true for the record function catch it.
        CloseCallEvent.set()
        StopRecordEvent.set()
        session.pop("started_call", None)
        return jsonify({})


def execute_routes(app, data_storage):  # Function that executes all the routes.
    general_routes(app, data_storage)  # General pages navigation
    attack_generation_routes(app, data_storage)  # Attack generation pages navigation
    error_routes(app)  # Errors pages navigation
