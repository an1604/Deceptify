import pyaudio
import wave
import numpy as np


def play_audio_through_vbcable(audio_file_path):
    # Open the audio file
    wf = wave.open(audio_file_path, 'rb')

    # Instantiate PyAudio
    p = pyaudio.PyAudio()

    # Open a stream with the same format as the audio file
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Read data in chunks
    chunk = 1024
    data = wf.readframes(chunk)

    # Play the audio file
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    # Stop stream
    stream.stop_stream()
    stream.close()

    # Close PyAudio
    p.terminate()

    # Close the audio file
    wf.close()


if __name__ == "__main__":
    audio_file_path = 'C:\\colman\\Deceptify\\Server\\AudioFiles\\testFool.wav'  # Replace with your audio file path
    play_audio_through_vbcable(audio_file_path)
