import logging
import os.path
import uuid
import urllib
from flask import redirect as flask_redirect, jsonify, session, render_template, url_for, flash, request
from werkzeug.utils import secure_filename
from flask_login import login_required
from threading import Thread
from app.Server.LLM.llm import llm
from app.Server.Forms.general_forms import *
from app.Server.Forms.upload_data_forms import *
from app.Server.Util import *
from app.Server.data.prompt import Prompt
from app.Server.data.AiAttack import AiAttack
from app.Server.speechToText import SRtest
from app.Server.run_bark import generateSpeech
from app.Server.LLM.llm_chat_tools.send_email import send_email
from app.main.main_params import MainRotesParams

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def attack_generation_routes(main, data_storage, file_manager, socketio):
    @main.route("/new_ai_attack", methods=["GET", "POST"])
    @login_required
    def new_ai_attack():
        form = AiAttackForm()
        if form.validate_on_submit():
            campaign_name = form.campaign_name.data
            target_name = form.target_name.data
            message_type = form.message_type.data
            message_name = form.message_name.data
            attack_purpose = form.attack_purpose.data
            place = form.place.data
            attack_id = int(uuid.uuid4()) % 1000
            attack = AiAttack(
                campaign_name,
                target_name,
                message_type,
                message_name,
                attack_purpose,
                place,
                attack_id,
            )
            data_storage.add_ai_attack(attack)
            logging.info(f"New AI attack created: {attack_id} for campaign {campaign_name}.")
            return flask_redirect(url_for("main.zoom_authorization", id=attack_id))
        return render_template('attack_pages/new_ai_attack.html', form=form)

    @main.route("/new_clone_attack", methods=["GET", "POST"])
    @login_required
    def new_clone_attack():
        form = CloneAttackForm()
        if form.validate_on_submit():
            logging.info("Clone attack form submitted successfully.")
            return None
        return render_template("attack_pages/new_voice_attack.html", form=form)

    @main.route('/attack_dashboard_transition', methods=['GET'])
    @login_required
    def attack_dashboard_transition():
        zoom_url = urllib.parse.unquote(request.args.get('start_url'))
        password = request.args.get('password')

        logging.info(f"Transition to attack dashboard with Zoom URL: {zoom_url} and password.")

        attack_id = session.get('whatsapp_attack_info').get('attack_id')
        if session.get("started_call"):
            session.pop("started_call")
        return render_template('attack_pages/attack_dashboard_transition.html',
                               id=attack_id, zoom_url=zoom_url, password=password)

    @main.route('/results_redirect', methods=['GET'])
    @login_required
    def results_redirect():
        is_success = request.args.get('is_success')
        is_success = str(is_success).lower()
        logging.info(f"Redirecting to results with success status: {is_success}")
        return flask_redirect(url_for('main.download_page', is_success=is_success))

    @main.route('/start_attack', methods=['GET', 'POST'])
    @login_required
    def start_attack():
        attack_id = request.args.get('attack_id')
        attack = data_storage.get_ai_attack(attack_id)
        logging.info(f"Starting attack with ID: {attack_id}")

        MainRotesParams.StopRecordEvent.clear()
        MainRotesParams.StopBackgroundEvent.clear()
        recorder_thread = Thread(target=record_call, args=(MainRotesParams.StopRecordEvent, "recording.wav"))
        recorder_thread.start()
        time.sleep(1)

        is_success = SRtest.startConv(file_manager.audios_dir, attack.get_attack_prompts(), attack.getPurpose(),
                                      "Hello " + attack.getTargetName().split(" ")[
                                          0] + " this is Jason from " + attack.getPlace() +
                                      " " + attack.getPurpose(), MainRotesParams.StopRecordEvent, attack.target_name)
        recorder_thread.join()
        logging.info(f"Attack {attack_id} completed with success status: {is_success}")

        file_manager.rename_file('attack_records', 'recording.wav', "recording" + str(attack.getID()) + ".wav")
        file_manager.rename_file('attack_records', 'transcript.txt', "transcript" + str(attack.getID()) + ".txt")
        attack.setResult(is_success)
        attack.setRec(file_manager.attack_records_dir + "recording" + str(attack.getID()) + ".wav")
        attack.setTranscript(file_manager.attack_records_dir + "transcript" + str(attack.getID()) + ".txt")

        return jsonify({'is_success': is_success})

    @main.route('/attack_dashboard', methods=['GET', 'POST'])
    @login_required
    def attack_dashboard():
        global cam_thread
        profile_name = request.args.get("profile")
        contact_name = request.args.get("contact")
        attack_id = request.args.get("id")

        logging.info(
            f"Accessing attack dashboard for profile: {profile_name}, contact: {contact_name}, attack ID: {attack_id}")

        profile = data_storage.get_profile(profile_name)
        attack = profile.get_attack(attack_id)
        attack_purpose = "address"
        form = AttackDashboardForm()
        form.prompt_field.choices = [(prompt.prompt_desc, prompt.prompt_desc) for prompt in profile.getPrompts()]

        started = session.get("started_call")
        if not started:
            recorder_thread = Thread(target=record_call,
                                     args=(MainRotesParams.StopRecordEvent, "Attacker-" + profile_name +
                                           "-Target-" + contact_name))
            recorder_thread.start()
            session["started_call"] = True
            session['stopped_call'] = False
            logging.info("Call recording started.")
        if form.validate_on_submit():
            play_audio_through_vbcable(
                file_manager.get_file_from_audio_dir(f"{profile_name}-{form.prompt_field.data}.wav"))
            logging.info(f"Playing audio through VB-Cable: {form.prompt_field.data}")
            return flask_redirect(url_for('main.attack_dashboard', profile=profile_name,
                                          contact=contact_name, id=attack_id))
        return render_template('attack_pages/attack_dashboard.html', form=form,
                               contact=contact_name, id=attack_id)
    # Additional routes with logging...
