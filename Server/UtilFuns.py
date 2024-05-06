# Importing the necessary libraries
import sounddevice as sd
import soundfile as sf


# import pyaudio

# def pygrabAudioIO():
#     """
#     Function to grab audio input and output devices
#     """
#
#     p = pyaudio.PyAudio()
#
#     # Getting the default input and output devices
#     input_device = p.get_default_input_device_info()
#     output_device = p.get_default_output_device_info()
#
#     # Returning the input and output devices
#     return input_device, output_device

def grabAudioIO():
    """
    Function to grab audio input and output devices
    """

    # Getting the default input and output devices
    input_device = sd.default.device[0]
    output_device = sd.default.device[1]

    # Returning the input and output devices
    return input_device, output_device


# TODO: either add to bellow or create new method for self recording
def recordConvo(input_device, output_device):
    """
    Function to record the conversation
    """
    print("recordConvo called!")

    # Getting the sample rate
    sample_rate = 44100

    # Getting the duration of recording
    duration = 10

    # Recording the conversation
    recording = sd.rec(int(duration), samplerate=sample_rate, channels=1,
                       device=(input_device, output_device))

    print(f"recordConvo Function done, output is: {recording} ")
    # Returning the recording
    return recording, sample_rate
# main to test methods
# if __name__ == '__main__':
#    inout = grabAudioIO()
#    print(recordConvo(inout[0],inout[1]))

