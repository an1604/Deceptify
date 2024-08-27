import time
from threading import Thread, Event
from queue import Queue
from app.Server.Util import *
from speech_recognition import WaitTimeoutError
import pyaudio
from app.Server.Util import generate_voice, get_voice_profile, play_audio_through_vbcable, play_background
from app.Server.speechToText.utilities_for_s2t import *
import re
from app.Server.data.DataStorage import Data
from app.Server.LLM.llm import llm
from app.Server.run_bark import generateSpeech
import requests

r = sr.Recognizer()
audio_queue = Queue()
flag = False
waitforllm = Event()
data_storage = Data().get_data_object()
prompts_for_user = set()
llm_thread = None
llm_flag = True


def get_device_index(device_name="CABLE Output"):
    p = pyaudio.PyAudio()
    device_index = None
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if device_name in dev['name']:
            print(device_name)
            device_index = i
            break
    p.terminate()
    return device_index


def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename).strip()


def recognize_worker(config, username, backgroundEvent):
    global flag, waitforllm, data_storage, prompts_for_user
    fillers = ["Wait a second umm", "Let me check umm", "Hold on a second umm"]
    index = 0
    time.sleep(3)
    while llm_flag:
        audio = audio_queue.get()  # Retrieve the next audio processing job from the main thread
        if audio is None:
            break  # Stop processing if the main thread is done
        # Recognize audio data using Google Speech Recognition
        try:
            spoken_text = r.recognize_google(audio)
            backgroundEvent.clear()
            print("User says: " + spoken_text)
            response = llm.get_answer(spoken_text).strip()
            print("AI says: " + response)
            if "goodbye" in response.lower():
                flag = True
            if response in prompts_for_user:
                background_thread = Thread(target=play_background, args=(backgroundEvent,
                                                                         config['UPLOAD_FOLDER']
                                                                         + "\\office.wav",))
                background_thread.start()
                play_audio_through_vbcable(config['UPLOAD_FOLDER'] + "\\" +
                                           response + ".wav")
                backgroundEvent.set()
            else:
                sanitized_prompt = sanitize_filename(response)
                background_thread = Thread(target=play_background, args=(backgroundEvent,
                                                                         config['UPLOAD_FOLDER']
                                                                         + "\\office.wav",))
                background_thread.start()
                start_filler = Thread(target=play_audio_through_vbcable,
                                      args=(config['UPLOAD_FOLDER'] + "\\" +
                                            fillers[index] + ".wav", "CABLE Input"))
                start_filler.daemon = True
                start_filler.start()
                index = (index + 1) % 3
                generateSpeech(text_prompt=response,
                               path=config['UPLOAD_FOLDER'] + "\\prompt.wav")
                play_audio_through_vbcable(config['UPLOAD_FOLDER'] + "\\prompt.wav")
                backgroundEvent.set()
            if not waitforllm.is_set():
                waitforllm.set()
        except sr.UnknownValueError:
            waitforllm.set()
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            waitforllm.set()
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        except Exception as e:
            waitforllm.set()
            print(f'Exception from recognize_worker: {e}')


def startConv(config, attack_prompts, purpose, starting_message, record_event, target_name,
              username="oded"):
    global flag, waitforllm, prompts_for_user, r, stop_listening, llm_thread
    backgroundEvent = Event()
    llm.initialize_new_attack(attack_purpose=purpose, profile_name=target_name)  # Refine the llm to the new attack
    flag = False
    started_conv = False
    prompts_for_user = attack_prompts

    llm_thread = Thread(target=recognize_worker, args=(config, username, backgroundEvent,))
    llm_thread.daemon = True
    llm_thread.start()
    device_index = get_device_index()
    try:
        print("source")
        with sr.Microphone() as source:
            print("Adjusting for ambient noise, please wait...")
            print("Listening for speech...")
            # r.adjust_for_ambient_noise(source)
            while not flag:
                try:
                    waitforllm.clear()
                    if not started_conv:
                        background_thread = Thread(target=play_background, args=(backgroundEvent,
                                                                                 config['UPLOAD_FOLDER']
                                                                                 + "\\office.wav",))
                        background_thread.start()
                        play_audio_through_vbcable(config['UPLOAD_FOLDER'] + "\\" +
                                                   starting_message + ".wav", "CABLE Input")
                        backgroundEvent.set()
                        # need to generate on attack phase
                        llm.chat_history.add_ai_response(starting_message)
                        print("AI says: " + starting_message)
                        started_conv = True
                    # r.pause_threshold = 1
                    audio_queue.put(r.listen(source, timeout=8, phrase_time_limit=8))
                    print("sleeping")
                    waitforllm.wait()
                    print("Woke up")
                except WaitTimeoutError:
                    print("Timed out waiting for audio")
                    continue
    except Exception as e:
        print(e)
        raise e
    print("did not recognize source")
    record_event.set()
    backgroundEvent.set()
    is_success = None
    final_msg = llm.get_finish_msg()
    if purpose == "Bank":
        if final_msg == "Thank you, we have solved the issue. Goodbye":
            is_success = True
        else:
            is_success = False
    elif purpose == "Hospital":
        if final_msg == "Thank you, we have opened your account. Goodbye":
            is_success = True
        else:
            is_success = False
    else:
        is_success = llm.get_answer(
            "Based on your history can you tell me with a true or false answer if the person gave you its address")
        if is_success.lower() == "true":
            is_success = True
        else:
            is_success = False
    stop()
    return is_success
