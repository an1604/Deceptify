from threading import Thread, Event
from queue import Queue
from app.Server.Util import *
from speech_recognition import WaitTimeoutError
import pyaudio
from app.Server.Util import play_audio_through_vbcable, play_background
import re
from app.Server.data.DataStorage import Data
from app.Server.LLM.llm import llm
from app.Server.run_bark import generateSpeech
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

r = sr.Recognizer()
audio_queue = Queue()
flag = False
waitforllm = Event()
data_storage = Data().get_data_object()
prompts_for_user = set()
recognize_thread = None
llm_flag = True
background_thread = None


def get_device_index(device_name="CABLE Output"):
    p = pyaudio.PyAudio()
    device_index = None
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if device_name in dev['name']:
            logging.info(f"Found device: {device_name}")
            device_index = i
            break
    p.terminate()
    return device_index


def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename).strip()


def recognize_worker(audios_dir, username, backgroundEvent):
    global flag, waitforllm, data_storage, prompts_for_user, background_thread
    fillers = ["Wait a second umm", "Let me check umm", "Hold on a second umm"]
    index = 0
    time.sleep(2)
    while llm_flag:
        audio = audio_queue.get()
        if audio is None:
            break
        try:
            spoken_text = r.recognize_google(audio)
            backgroundEvent.clear()
            logging.info(f"User says: {spoken_text}")
            response = llm.get_answer_from_embedding(spoken_text)

            if response is None:
                response = llm.validate_number(spoken_text)
                if response is None:
                    background_thread = Thread(target=play_background,
                                               args=(backgroundEvent, audios_dir + "\\office.wav",))
                    background_thread.start()
                    start_filler = Thread(target=play_audio_through_vbcable,
                                          args=(audios_dir + "\\" + fillers[index] + ".wav", "CABLE Input"))
                    start_filler.daemon = True
                    start_filler.start()
                    index = (index + 1) % 3
                    response = llm.get_answer(spoken_text).strip()
                else:
                    llm.chat_history.add_ai_response(response)
                    llm.finish_msg = response
                    llm.end_conv = True
            response.strip()

            logging.info(f"AI says: {response}")

            if "goodbye" in response.lower():
                flag = True

            if response in prompts_for_user:
                background_thread = Thread(target=play_background, args=(backgroundEvent, audios_dir + "\\office.wav",))
                background_thread.start()
                play_audio_through_vbcable(audios_dir + "\\" + response + ".wav")
                backgroundEvent.set()
                background_thread = None

            else:
                if background_thread is None:
                    background_thread = Thread(target=play_background,
                                               args=(backgroundEvent, audios_dir + "\\office.wav",))
                    background_thread.start()
                    start_filler = Thread(target=play_audio_through_vbcable,
                                          args=(audios_dir + "\\" + fillers[index] + ".wav", "CABLE Input"))
                    start_filler.daemon = True
                    start_filler.start()
                    index = (index + 1) % 3
                generateSpeech(text_prompt=response, path=audios_dir + "\\prompt.wav")
                play_audio_through_vbcable(audios_dir + "\\prompt.wav")
                backgroundEvent.set()
                background_thread = None

            if not waitforllm.is_set():
                waitforllm.set()

        except (sr.UnknownValueError, sr.RequestError):
            waitforllm.set()
            logging.error("Google Speech Recognition could not understand audio")
        except Exception as e:
            waitforllm.set()
            logging.error(f'Exception from recognize_worker: {e}')
        finally:
            logging.info("Processing completed in recognize_worker")


def startConv(audios_dir, attack_prompts, purpose, starting_message, record_event, target_name, username="oded"):
    global flag, waitforllm, prompts_for_user, r, recognize_thread, llm_flag
    llm_flag = True
    backgroundEvent = Event()
    llm.initialize_new_attack(attack_purpose=purpose, profile_name=target_name)
    flag = False
    started_conv = False
    prompts_for_user = attack_prompts

    recognize_thread = Thread(target=recognize_worker, args=(audios_dir, username, backgroundEvent,))
    recognize_thread.daemon = True
    recognize_thread.start()
    device_index = get_device_index()

    with sr.Microphone() as source:
        logging.info("Adjusting for ambient noise, please wait...")
        logging.info("Listening for speech...")
        while not flag:
            try:
                waitforllm.clear()
                if not started_conv:
                    background_thread = Thread(target=play_background,
                                               args=(backgroundEvent, audios_dir + "\\office.wav",))
                    background_thread.start()
                    play_audio_through_vbcable(audios_dir + "\\" + starting_message + ".wav", "CABLE Input")
                    backgroundEvent.set()
                    llm.chat_history.add_ai_response(starting_message)
                    logging.info(f"AI says: {starting_message}")
                    started_conv = True
                audio_queue.put(r.listen(source, timeout=8, phrase_time_limit=8))
                logging.info("Sleeping")
                waitforllm.wait()
                logging.info("Woke up")
            except WaitTimeoutError:
                logging.warning("Timed out waiting for audio")
                continue

    record_event.set()
    backgroundEvent.set()
    is_success = None
    final_msg = llm.get_finish_msg()
    logging.info(f"Final message: {final_msg}")
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

    return stop(is_success)


def stop(is_success=None):
    global flag, llm_flag, recognize_thread
    logging.info("stop() called!")

    llm.flush()
    flag = True
    waitforllm.set()
    llm_flag = False
    audio_queue.put(None)
    if recognize_thread:
        recognize_thread.join()
    return is_success
