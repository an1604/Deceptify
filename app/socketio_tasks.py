import logging
import threading

from flask_socketio import emit
from app.Server.LLM.llm_chat_tools.telegramclienthandler import TelegramClientHandler, TelegramInfo
from app.Server.Util import clone
from app.Server.speechToText.SRtest import stop

thread_lock = threading.Lock()  # Background thread Lock for all the tasks.
thread = None  # The main thread that will be run and perform the background tasks.

client = None

client_auth_event = threading.Event()  # Event for detecting client authentication with Telegram

auth_code_set_event = threading.Event()  # Event that alerted when the client received the authentication code.
code = None  # The authentication code as a global variable.

new_message_event = threading.Event()  # Event for a new message that needs to be sent.
message_tuple = None  # A tuple for the new message: (receiver, message content)

new_audio_event = threading.Event()  # Event for new audio generation request from the client.
audio_tuple = None  # A tuple for the audio generation process: (tts, receiver)

ask_for_new_messages_event = threading.Event()  # Event for a new messages update request.
new_messages = None  # Will be a list of the new messages from the Telegram client in real time.

telegram_info = None  # An object that will be updated with the client's information.
telegram_info_event = threading.Event()  # The event that will be triggered the first initialization pf the client's information.


async def manual_send_message(receiver, message):
    global client
    await client.send_message(receiver, message)


async def manual_send_audio(receiver, audio):
    global client
    await client.send_audio(receiver, audio)


def background_thread(socketio):
    print("Starting background thread...")
    global new_message_event, message_tuple
    global audio_tuple, new_audio_event
    global ask_for_new_messages_event, new_messages
    global client_auth_event
    global auth_code_set_event, code
    global telegram_info_event, telegram_info
    global client

    print("Client connected but not set!")
    while True:
        if telegram_info_event.is_set() and telegram_info is not None:
            telegram_info_event.clear()
            try:
                client = TelegramClientHandler(telegram_info.app_id, telegram_info.app_hash, telegram_info.phone_number,
                                               client_auth_event, telegram_info.qr_path)
                telegram_info.is_connected = True

                socketio.emit("client_auth")  # Send an alert to update the client to check for an authorization code

                client.loop.run_until_complete(  # Run the method
                    # that will authorize with the provided code from the client.
                    client.authenticate_client_via_msg(0)
                )
                socketio.emit('connection_update', {'data': True})  # Update the front
                # after the process done successfully.
            except Exception as e:
                print(f"Exception from background_thread --> {e}")
                socketio.emit('connection_update', {'data': False})

        socketio.sleep(3)

        if new_message_event.is_set() and message_tuple is not None:
            new_message_event.clear()

            client.loop.run_until_complete(
                manual_send_message(message_tuple[0], message_tuple[1]))

            socketio.emit('server_update',
                          {'data': f'Message {message_tuple[1]} Successfully Sent to {message_tuple[0]} :)'})
            message_tuple = None
        if new_audio_event.is_set() and audio_tuple is not None:
            new_audio_event.clear()
            client.loop.run_until_complete(
                manual_send_audio(audio_tuple[0], audio_tuple[1])
            )
            socketio.emit('server_update',
                          {'data': f'Record {audio_tuple[1]} Successfully Sent to {audio_tuple[0]} :)'})
        if ask_for_new_messages_event.is_set():
            ask_for_new_messages_event.clear()
            new_messages = client.get_messages()

            socketio.emit('server_update',
                          {'data': 'New messages requests handled'})


def initialize_socketio(socketio, file_manager):
    print("Inside initialize_socketio")

    @socketio.on("connect_event")
    def connect_event(data):
        global thread, thread_lock, telegram_info

        # This event is called from the HTML page, so we need to make sure we need to run the code below
        # only when there is a problem with the client initialization.

        response = data['data']
        print(f"New client said: {response}")
        with thread_lock:
            if thread is None:
                thread = socketio.start_background_task(background_thread, socketio)

    @socketio.on("new_message")
    def handle_new_message(data):
        global message_tuple
        print(f"handle_new_message called --> {data}")
        receiver, message = data['receiver'], data['message']
        message_tuple = (receiver, message)
        new_message_event.set()
        emit("server_update",
             {'data': f"Request to send message to {message_tuple[0]} with content: {message_tuple[1]}"},
             broadcast=True)

    @socketio.on("new_audio_gen_req")
    def handle_audio_generation_status(data):
        logging.info('new_audio_gen_req handler called from front')
        profile_name_for_tts = data['profile_name_for_tts']
        tts = data['tts']

        logging.info("Send the cloning request to the remote server...")
        audio_path = clone(tts, profile_name_for_tts,
                           file_manager.get_new_audiofile_path_from_profile_name(profile_name_for_tts,
                                                                                 f'{tts.lower().replace(" ", "_")}.wav'),
                           file_manager.audios_dir)
        if audio_path:
            logging.info(f"Audio generated to {audio_path}")
            emit("new_audio", {"tts": tts, "audio_path": audio_path},
                 broadcast=True)
        else:
            logging.error("Error while trying to generate the speech from remote server")
            emit('server_update', {
                'data': "There was a problem while generating the audio, please try again. "
            })

    @socketio.on("client_audio_decision")
    def handle_audio_decision(data):
        global new_audio_event, audio_tuple
        action, audio, receiver = data['action'], data['audio'], data['receiver']
        if action == "accept":
            audio_tuple = (receiver, audio)
            new_audio_event.set()
            emit("server_update", {'data': "Client has accepted the audio"},
                 broadcast=True)
        else:
            emit("server_update", {'data': 'Client has not accepted the audio'},
                 broadcast=True)

    @socketio.on('ask_for_new_messages')
    def handle_ask_for_new_messages():
        global ask_for_new_messages_event, new_messages
        ask_for_new_messages_event.set()
        print(f"from handle_ask_for_new_messages --> {new_messages}")
        emit("new_messages_update",
             {'data': new_messages},
             broadcast=True)

    @socketio.on("auth_code")
    def handle_auth_code(data):
        global client
        client.auth_code = data['code']
        emit("server_update", {
            'data': "Authentication request sent."
        })

    @socketio.on("init_client")
    def handle_init_client(data):
        global thread, thread_lock
        global telegram_info_event, telegram_info

        app_id = data['app_id']
        app_hash = data['app_hash']
        profile_name = data['profile_name']
        phone_number = data['phone_number']

        telegram_info = TelegramInfo(app_id, app_hash, profile_name, phone_number,
                                     file_manager.get_unique_qr_path(profile_name))
        telegram_info_event.set()
        print(f"{profile_name} initialized!")

        emit("server_update", {
            'data': "AUTHENTICATION REQUEST RECEIVED"
        })

    @socketio.on("stop_attack")
    def handle_stop_attack():
        print("from socketio: stop_attack triggered and runs stop() function.")
        stop()

    @socketio.on('auth_code_timeout')
    def handle_auth_code_timeout():
        global client

        client.is_client_connected = True
        emit("server_update", {
            'data': "Your account seems to be authorized yet, released the send"
                    "authentication code request, you can try to run the attack now :)"
        })

    @socketio.on("connection_update")
    def handle_connection_update():
        global client

        emit("connection_update", {
            'data': client.is_connected
        })
