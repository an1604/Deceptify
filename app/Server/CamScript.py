import cv2
import pyvirtualcam

# Open video file
video_path = 'result_voice.mp4'  # Replace with your video file path
video = cv2.VideoCapture(video_path)

if not video.isOpened():
    print("Error: Could not open video.")
    exit()

# Get video properties
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = video.get(cv2.CAP_PROP_FPS)

# Open virtual camera
with pyvirtualcam.Camera(width, height, fps, fmt=pyvirtualcam.PixelFormat.BGR) as cam:
    print(f'Using virtual camera: {cam.device}')

    while True:
        ret, frame = video.read()
        if not ret:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Send frame to virtual camera
        cam.send(frame)

        # Wait until next frame is due
        cam.sleep_until_next_frame()

video.release()
