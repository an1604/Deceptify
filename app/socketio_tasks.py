from flask_socketio import SocketIO, emit


def get_dynamic_updates(socketio):
    pass


def run_socketio_tasks(socketio, socketio_thread_lock, socketio_thread=None):
    @socketio.event
    def connect():
        global socketio_thread
        print('Client connected')
        with socketio_thread_lock:
            if socketio_thread is None:
                socketio_thread = socketio.start_background_task(get_dynamic_updates, socketio)
        emit('update', {'data': 'Connected', 'count': 0})

    @socketio.on('telegram_update')
    def handle_telegram_update(data):
        emit('update', {'data': data, 'count': 0})

    # TODO: ADD MORE REALTIME UPDATES AND COMMUNICATIONS, SUCH AS REALTIME LOGS FOR THE VOICE ATTACK
