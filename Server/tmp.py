import json
import random
import time
import speech_recognition as sr

conversation = {'user': {}, 'model': {}}
global filename

# this is called from the background thread
def convert(recognizer, audio):
    global filename
    if filename:  # Checks if the filename var filled already.
        try:
            msg = recognizer.recognize_google(audio)
            print("Speech Recognition Agent thinks you said " + msg)

            # Saving the conversion into dictionary to write it into file.
            conversation['target'][time.time()] = msg

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))


def s2t(fname:str):
    try:
        # filename = 'transcript.json'
        global filename
        filename = fname + '.json'  # Opening some file to write the transcript
        filename2 = 'conversations/' + filename  # Navigate the target file to the directory.

        r = sr.Recognizer()
        m = sr.Microphone()
        print("Say something!")

        with m as source:
            r.adjust_for_ambient_noise(source)  # calibrate once, before we start listening

        stop_listening_func = r.listen_in_background(m,
                                                     convert)  # Running a background thread for converting the speech into text.

        for _ in range(50):  # Wasting time in the main thread for 5 seconds.
            time.sleep(0.2)  # The main thread is doing other things.

        counter = 0
        rnd = random.randint(1, 10000)
        while counter + rnd != 0:  # Doing some stuff while the other thread converting speech to text.
            counter = random.randint(1, 10000)

    except KeyboardInterrupt:
        stop_listening_func(wait_for_stop=False)
        with open(filename2, 'w') as audio_file:
            json.dump(conversation, audio_file)
            print(f"Conversation transcript saved on: {filename2}")
    except Exception as e:
        stop_listening_func(wait_for_stop=False)
        print(f'Error: {e}')