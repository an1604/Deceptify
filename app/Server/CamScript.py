import cv2
import pyvirtualcam
from threading import Event
import time

virtual_cam = None


def connect(width, height, fps, event):
    global virtual_cam
    while virtual_cam is None:
        try:
            virtual_cam = pyvirtualcam.Camera(width, height, fps, fmt=pyvirtualcam.PixelFormat.BGR, backend='obs')
            print(f'Connected to virtual camera: {virtual_cam.device}')
        except RuntimeError as e:
            print(f"RuntimeError: {e}")


def ResetVirtualCam():
    global virtual_cam
    virtual_cam = None


def RunVideo(video_path, is_default: bool, event: Event):
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print("Error: Could not open video.")
        exit()
    event.clear()
    # Get video properties
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)
    if virtual_cam is None:
        connect(width, height, fps, event)
    print("starting video")
    while not event.is_set():
        ret, frame = video.read()
        if not ret:
            if not is_default:
                return
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        # Send frame to virtual camera
        virtual_cam.send(frame)

        # Wait until next frame is due
        virtual_cam.sleep_until_next_frame()
    print("ending video")
    video.release()
