# Importing the necessary libraries
import sounddevice as sd
import soundfile as sf


def grabAudioIO():
    """
    Function to grab audio input and output devices
    """

    # Getting the list of audio devices
    devices = sd.query_devices()
    print(devices)

    # Getting the input and output devices
    input_device = int(input("Relevant Deceptify input "))
    output_device = int(input("Relevant Deceptify output "))

    # Returning the input and output devices
    return input_device, output_device


def recordConvo(input_device, output_device):
    """
    Function to record the conversation
    """

    # Getting the sample rate
    sample_rate = 44100

    # Getting the duration of recording
    duration = 10

    # Recording the conversation
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2,
                       device=(input_device, output_device))

    # Returning the recording
    return recording, sample_rate
