from threading import Thread
from queue import Queue
from app.Server.Util import *
from speech_recognition import WaitTimeoutError
from app.Server.LLM.llm import Llm

from app.Server.Util import generate_voice, get_voice_profile, play_audio_through_vbcable
from app.Server.speechToText.utilities_for_s2t import *

r = sr.Recognizer()
audio_queue = Queue()
conversation_history = []
flag = False
llm = Llm()
isAnswer = None


def recognize_worker(config, profile_name, username):
    global flag
    # This runs in a background thread
    global isAnswer
    while True:
        audio = audio_queue.get()  # Retrieve the next audio processing job from the main thread
        if audio is None:
            break  # Stop processing if the main thread is done

        # Recognize audio data using Google Speech Recognition
        try:
            spoken_text = r.recognize_google(audio)
            print("User said: " + spoken_text)
            conversation_history.append({"user": spoken_text})
            isAnswer = False
            response = llm.get_answer(spoken_text)
            isAnswer = True
            print("AI says: " + response)
            for phrase in end_call_phrases:
                if phrase in response:
                    flag = True
            serv_response = generate_voice(username, profile_name, response)
            get_voice_profile(username, profile_name, response, serv_response["file"])
            play_audio_through_vbcable(config['UPLOAD_FOLDER'] + "\\" + profile_name + "-" +
                                       response + ".wav")
            conversation_history.append({"ai": response})
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        except Exception as e:
            print(e)


def startConv(config, profile_name, username="oded"):
    global flag
    recognize_thread = Thread(target=recognize_worker, args=(config, profile_name, username,))
    recognize_thread.daemon = True
    recognize_thread.start()

    with sr.Microphone() as source:
        print("Adjusting for ambient noise, please wait...")
        print("Listening for speech...")
        print(source)
        try:
            while not flag:
                r.adjust_for_ambient_noise(source)
                # r.pause_threshold = 1
                audio_queue.put(r.listen(source, timeout=8, phrase_time_limit=8))
                print("sleeping")
                time.sleep(10)
                if not isAnswer:
                    # Generate filler
                    pass
                print("Woke up")

        except WaitTimeoutError:
            print("Timed out waiting for audio")

    save_conversation_to_json("conversation.json", conversation_history)
    audio_queue.join()  # Block until all current audio processing jobs are done
    audio_queue.put(None)  # Tell the recognize_thread to stop
    recognize_thread.join()  # Wait for the recognize_thread to actually stop
