import json
import random
import time
import speech_recognition as sr


class SpeechToText:
    """
    A class used to convert speech to text and save the conversation.

    ...

    Attributes
    ----------
    filename : str
        the name of the file where the conversation will be saved
    conversation : dict
        a dictionary to store the conversation

    Methods
    -------
    convert(recognizer, audio):
        Converts the speech from the audio to text using Google's Speech Recognition.
    start():
        Starts the speech recognition process.
    """

    def __init__(self, filename):
        """
        Constructs all the necessary attributes for the SpeechToText object.

        Parameters
        ----------
            filename : str
                the name of the file where the conversation will be saved
        """
        self.filename = filename
        self.conversation = {'user': {}, 'model': {}}

    def convert(self, recognizer, audio):
        """
        Converts the speech from the audio to text using Google's Speech Recognition.

        Parameters
        ----------
            recognizer : Recognizer
                the recognizer instance to use
            audio : AudioData
                the audio data to be recognized
        """
        try:
            msg = recognizer.recognize_google(audio)
            print("Speech Recognition Agent thinks you said " + msg)
            self.conversation['user'][time.time()] = msg
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

    def start(self):
        """
        Starts the speech recognition process.
        """
        try:
            r = sr.Recognizer()
            m = sr.Microphone()
            print("Say something!")

            with m as source:
                r.adjust_for_ambient_noise(source)

            stop_listening_func = r.listen_in_background(m, self.convert)

            for _ in range(50):
                time.sleep(0.2)

            counter = 0
            rnd = random.randint(1, 10000)
            while counter + rnd != 0:
                counter = random.randint(1, 10000)

        except KeyboardInterrupt:
            stop_listening_func(wait_for_stop=False)
            with open(f'conversations/{self.filename}.json', 'w') as audio_file:
                json.dump(self.conversation, audio_file)
                print(f"Conversation transcript saved on: conversations/{self.filename}.json")
        except Exception as e:
            stop_listening_func(wait_for_stop=False)
            print(f'Error: {e}')
