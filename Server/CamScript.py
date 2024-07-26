import cv2
import pyvirtualcam
from threading import Event


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

    # Open virtual camera
    with pyvirtualcam.Camera(width, height, fps, fmt=pyvirtualcam.PixelFormat.BGR) as cam:
        print(f'Using virtual camera: {cam.device}')

        while not event.is_set():
            ret, frame = video.read()
            if not ret:
                if not is_default:
                    return
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # Send frame to virtual camera
            cam.send(frame)

            # Wait until next frame is due
            cam.sleep_until_next_frame()

    video.release()
