import time
from threading import Thread, Event
from queue import Queue
from app.Server.Util import *
from speech_recognition import WaitTimeoutError
import pyaudio
from app.Server.Util import generate_voice, get_voice_profile, play_audio_through_vbcable
from app.Server.speechToText.utilities_for_s2t import *
import re
from app.Server.data.DataStorage import Data
from app.Server.LLM.llm import llm

r = sr.Recognizer()
audio_queue = Queue()
conversation_history = []
flag = False

waitforllm = Event()
data_storage = Data().get_data_object()
prompts_for_user = set()


def get_device_index(device_name="CABLE Output"):
    p = pyaudio.PyAudio()
    device_index = None
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if device_name in dev['name']:
            device_index = i
            break
    p.terminate()
    return device_index


def sanitize_filename(filename):
    # Replace invalid characters with underscores
    return re.sub(r'[<>:"/\\|?*]', '_', filename).strip()


def recognize_worker(config, profile_name, username, purpose):
    global flag, waitforllm, conversation_history, data_storage, prompts_for_user
    while True:
        audio = audio_queue.get()  # Retrieve the next audio processing job from the main thread
        if audio is None:
            break  # Stop processing if the main thread is done

        # Recognize audio data using Google Speech Recognition
        try:
            spoken_text = r.recognize_google(audio)
            conversation_history.append({"user": spoken_text})
            response = llm.get_answer(spoken_text, conversation_history).strip()
            print("AI says: " + response)

            if "see you" in response.lower():
                flag = True
            if response in prompts_for_user:
                play_audio_through_vbcable(config['UPLOAD_FOLDER'] + "\\" + profile_name + "-" +
                                           response + ".wav")
            else:
                sanitized_prompt = sanitize_filename(response)
                prompts_for_user.add(sanitized_prompt)
                #TODO: Add a filler of "wait a second", "hold on a second"
                serv_response = generate_voice(username, profile_name, sanitized_prompt)
                get_voice_profile(username, profile_name, "prompt", serv_response["file"])
                play_audio_through_vbcable(config['UPLOAD_FOLDER'] + "\\" + profile_name + "-" +
                                           "prompt" + ".wav")
            conversation_history.append({"ai": response})
            if response == "I am good thank you":
                time.sleep(1)
                print()
                #TODO: play audio file of, "can i have your email?","can i have your id?" etc
                # and add it to llm history
                play_audio_through_vbcable(config['UPLOAD_FOLDER'] + "\\" + profile_name + "-" +
                                           "Can i have your" +  + ".wav")
                conversation_history.append({"ai": response})
            elif response == "Thank you":
                time.sleep(1)
                play_audio_through_vbcable(config['UPLOAD_FOLDER'] + "\\" + profile_name + "-" +
                                           "See you later" + ".wav")
                flag = True
                conversation_history.append({"ai": "See you later"})
            if not waitforllm.is_set():
                waitforllm.set()
        except sr.UnknownValueError:
            waitforllm.set()
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            waitforllm.set()
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        except Exception as e:
            print(e)


def startConv(config, profile_name, purpose, username="oded", starting_message="Hello how are you doing"):
    global flag, waitforllm, prompts_for_user
    flag = False
    started_conv = False

    prompts_for_user = set([prompt.prompt_desc for prompt in
                            data_storage.get_profile(profile_name).getPrompts()])

    recognize_thread = Thread(target=recognize_worker, args=(config, profile_name, username,))
    recognize_thread.daemon = True
    recognize_thread.start()
    device_index = get_device_index()

    with sr.Microphone() as source:
        print("Adjusting for ambient noise, please wait...")
        print("Listening for speech...")
        try:
            while not flag:
                waitforllm.clear()
                r.adjust_for_ambient_noise(source)
                if not started_conv:
                    play_audio_through_vbcable(config['UPLOAD_FOLDER'] + "\\" + profile_name + "-" +
                                               starting_message + ".wav", "CABLE Input")
                    conversation_history.append({"ai": starting_message})
                    started_conv = True
                # r.pause_threshold = 1
                audio_queue.put(r.listen(source, timeout=8, phrase_time_limit=8))
                print("sleeping")
                waitforllm.wait()
                print("Woke up")

        except WaitTimeoutError:
            print("Timed out waiting for audio")
    llm.end_conversation()
    save_conversation_to_json(profile_name + "-conversation.json", conversation_history)
    audio_queue.join()  # Block until all current audio processing jobs are done
    audio_queue.put(None)  # Tell the recognize_thread to stop
    recognize_thread.join()  # Wait for the recognize_thread to actually stop
    starting_thread.join()
