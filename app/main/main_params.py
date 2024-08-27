import os
from threading import Event
from dotenv import load_dotenv

load_dotenv()


class MainRotesParams(object):
    CloseCallEvent = Event()
    StopRecordEvent = Event()
    CutVideoEvent = Event()
    GetAnswerEvent = Event()
    StopBackgroundEvent = Event()
    cam_thread = None
    UpdatesFromTelegramClientEvent = Event()

    # Credentials For Zoom API
    ZOOM_CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
    ZOOM_CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')
    ZOOM_ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')
    AUTH_URL = os.getenv('ZOOM_AUTH_URL')
    REDIRECT_URI = os.getenv('REDIRECT_URI')
    TOKEN_URL = os.getenv('TOKEN_URL')
    BASE_ZOOM_URL = os.getenv('BASE_ZOOM_API_REQ_URL')
