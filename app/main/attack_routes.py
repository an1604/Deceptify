import logging
import os.path
import uuid
import urllib
from flask import redirect as flask_redirect, jsonify, session, render_template, url_for, flash, \
    request
from werkzeug.utils import secure_filename
from flask_login import login_required
from threading import Thread
from app.Server.LLM.llm import llm

from app.Server.CamScript import ResetVirtualCam

from app.Server.Forms.general_forms import *
from app.Server.Forms.upload_data_forms import *
from app.Server.Util import *
from app.Server.data.prompt import Prompt
from app.Server.data.AiAttack import AiAttack
from app.Server.speechToText import SRtest
from app.Server.run_bark import generateSpeech
from app.Server.LLM.llm_chat_tools.send_email import send_email
from app.main.main_params import MainRotesParams

from app.Server.data.Profile import Profile


def attack_generation_routes(main, data_storage, file_manager, socketio):
    @main.route("/new_ai_attack", methods=["GET", "POST"])  # The new chat route.
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

            return flask_redirect(url_for("main.zoom_authorization", id=attack_id))
        return render_template('attack_pages/new_ai_attack.html', form=form)

    @main.route('/attack_dashboard_transition', methods=['GET'])
    @login_required
    def attack_dashboard_transition():
        zoom_url = urllib.parse.unquote(request.args.get('start_url'))
        password = request.args.get('password')

        print("zoom url is " + str(zoom_url))
        print(f'password is {password}')

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
        print("redirecting")
        return flask_redirect(url_for('main.download_page', is_success=is_success))

    @main.route('/results', methods=['GET'])
    @login_required
    def results():
        is_success = request.args.get('is_success')
        attack_id = request.args.get('id')
        return render_template('attack_pages/results.html', is_success=is_success, id=attack_id)

    @main.route('/generate_attack_type', methods=['GET'])
    @login_required
    def generate_attack_type():
        attack_id = request.args.get('attack_id')
        zoom_url = request.args.get('zoom_url')
        zoom_url = zoom_url.split('?')[0]
        password = request.args.get('password')
        attack = data_storage.get_ai_attack(attack_id)
        if attack.getPurpose() == "WhatsApp and Zoom":
            attack.attack_purpose = "Bank"
        attack_prompts = attack.get_attack_prompts()
        purpose = attack.getPurpose()
        place = attack.getPlace()
        contact = attack.getTargetName()
        if attack.getMessageType() == "Whatsapp":
            phone_number = attack.getMessageName()
            from app.Server.LLM.llm_chat_tools.whatsapp import WhatsAppBot
            WhatsAppBot.send_text_private_message(phone_number=phone_number,
                                                  message=WhatsAppBot.get_message_template(zoom_url, contact,
                                                                                           purpose, place, password))
        else:  # type is email
            from app.Server.LLM.llm_chat_tools.whatsapp import WhatsAppBot
            body = WhatsAppBot.get_message_template(zoom_url, contact, purpose, place, password)
            email = attack.getMessageName()
            send_email(email_receiver=email, email_subject="Immediate attention",
                       email_body=body,
                       display_name="" + place + " " + purpose,
                       from_email=f"{place.replace(' ', '')}@gmail.com")

        for prompt in attack_prompts:
            if not file_manager.prompt_rec_exists_in_audio_dir(prompt):
                generateSpeech(prompt, file_manager.get_file_from_audio_dir(f"\\{prompt}.wav"))

        starting_message = "Hello " + attack.getTargetName().split(" ")[
            0] + " this is Jason from " + attack.getPlace() + " " + attack.getPurpose() + " umm"
        if not file_manager.prompt_rec_exists_in_audio_dir(starting_message):
            path = file_manager.get_file_from_audio_dir(f"\\{starting_message}.wav")
            logging.info(f"From attack --> path is: {path}")
            generateSpeech(starting_message, path)
        return jsonify({"status": "complete"})

    @main.route('/start_attack', methods=['GET', 'POST'])
    @login_required
    def start_attack():
        attack_id = request.args.get('attack_id')
        attack = data_storage.get_ai_attack(attack_id)
        MainRotesParams.StopRecordEvent.clear()
        MainRotesParams.StopBackgroundEvent.clear()
        recorder_thread = Thread(target=record_call, args=(MainRotesParams.StopRecordEvent, "recording.wav"))
        recorder_thread.start()
        time.sleep(1)
        is_success = SRtest.startConv(file_manager.audios_dir, attack.get_attack_prompts(), attack.getPurpose(),
                                      "Hello " +
                                      attack.getTargetName().split(" ")[
                                          0] + " this is Jason from " + attack.getPlace() +
                                      " " + attack.getPurpose() + " umm", MainRotesParams.StopRecordEvent,
                                      attack.target_name)
        recorder_thread.join()
        file_manager.rename_file('attack_records', 'recording.wav', "recording" + str(attack.getID()) + ".wav")
        file_manager.rename_file('attack_records', 'transcript.txt', "transcript" + str(attack.getID()) + ".txt")
        attack.setResult(is_success)
        attack.setRec(file_manager.attack_records_dir + "recording" + str(attack.getID()) + ".wav")
        attack.setTranscript(file_manager.attack_records_dir + "transcript" + str(attack.getID()) + ".txt")
        print(is_success)
        return jsonify({'is_success': is_success})

    @main.route('/send_prompt', methods=['GET'])
    @login_required
    def send_prompt():
        prompt_path = request.args.get("prompt_path")
        return play_audio_through_vbcable(prompt_path)

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
        profile_name = request.args.get('profile_name')
        form = VoiceUploadForm()
        if form.validate_on_submit():
            profile_name_voice_dir = file_manager.get_file_from_audio_dir(profile_name + '-clone')
            file_manager.create_directory(profile_name_voice_dir)
            file = form.file.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(profile_name_voice_dir, filename)
            file.save(file_path)

            if create_voice_profile(username="oded", profile_name=profile_name,
                                    speaker_wavfile_path=file_path):
                data_storage.add_profile(Profile(profile_name, file_path))
                return flask_redirect(url_for("main.index"))
            else:
                flash("Something wrong, try again please")
        return render_template("data_collection_pages/upload_voice_file.html", form=form)

    @main.route(
        "/record_voice", methods=["GET", "POST"]
    )  # Route for record a new voice file.
    @login_required
    def record_voice():
        profile_name = request.args.get('profile_name')
        return render_template("data_collection_pages/record_voice.html", profile_name=profile_name)

    @main.route("/save-record", methods=["POST"])
    @login_required
    def save_record():
        print("start saving")
        if "file" not in request.files:
            flash("No file part")
            return flask_redirect(request.url)
        file = request.files["file"]
        profile_name = request.form.get("profile_name")
        if file.filename == "":
            flash("No selected file")
            return flask_redirect(request.url)
        file_name = f'{profile_name}_original_speech.wav'

        file_path = file_manager.get_new_audiofile_path_from_profile_name(profile_name, file_name)

        file.save(file_path)
        if create_voice_profile(username="oded", profile_name=profile_name,
                                speaker_wavfile_path=file_path):
            data_storage.add_profile(Profile(profile_name, file_path))
            return jsonify({
                'data': "success"
            }), 200
        return jsonify({
            'data': "failed"
        }), 500

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
        MainRotesParams.CloseCallEvent.set()
        MainRotesParams.StopRecordEvent.set()
        MainRotesParams.CutVideoEvent.set()
        ResetVirtualCam()
        session.pop("started_call", None)
        return jsonify({})

    @main.route('/init_chat_demo', methods=["GET", "POST"])
    def init_chat_demo():
        form = InitDemoForm()
        if form.validate_on_submit():
            attack_purpose = form.purpose.data
            profile_name = form.profile_name.data

            llm.initialize_new_attack(attack_purpose, profile_name)  # Initialize a new chat-demo attack.
            runs_on = form.runs_on.data
            if 'Local Chat' in runs_on:
                return flask_redirect(url_for('main.new_chat_demo'))
            elif 'Telegram' in runs_on:
                return flask_redirect(url_for('main.telegram_chat_demo'))
            else:
                pass
        return render_template('demos/init_chat_demo.html', form=form)

    @main.route('/telegram_chat_demo', methods=["GET", "POST"])
    def telegram_chat_demo():
        return render_template('demos/telegram_chat_demo.html')

    @main.route('/new_chat_demo', methods=["GET", "POST"])
    def new_chat_demo():
        form = DemoForm()
        if form.validate_on_submit():
            message_body = form.message.data
            session['message_body_for_demo'] = message_body
            return flask_redirect(url_for('main.existing_demo_chat'))
        return render_template('demos/new_demo_chat.html', form=form, init_msg=llm.get_init_msg())

    @main.route('/existing_demo_chat', methods=["GET", "POST"])
    def existing_demo_chat():
        form = DemoForm()
        if 'message_body_for_demo' in session:
            message_body = session['message_body_for_demo']
            llm.get_answer(message_body)
            session.pop('message_body_for_demo', None)
        elif form.validate_on_submit():
            message = form.message.data
            answer = llm.get_answer(message)
            if 'bye' in answer.lower() or 'bye' in message.lower():
                session.pop('message_body_for_demo', None)
                llm.flush()
                return flask_redirect(url_for('main.index'))
        return render_template('demos/existing_demo_chat.html', form=form, messages=llm.get_chat_history(),
                               init_msg=llm.get_init_msg())
