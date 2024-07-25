import pyaudio
import wave


def get_device_index(device_name):
    p = pyaudio.PyAudio()
    device_index = None
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if device_name in dev['name']:
            device_index = i
            break
    p.terminate()
    return device_index


def play_audio_through_vbcable(audio_file_path, device_name="CABLE Input"):
    # Open the audio file
    wf = wave.open(audio_file_path, 'rb')
    playback_name = "CABLE Input"
    # Instantiate PyAudio
    p = pyaudio.PyAudio()
    device_index = get_device_index(device_name)
    # Open a stream with the same format as the audio file
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=device_index)

    default_stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
    # Read data in chunks
    chunk = 1024
    data = wf.readframes(chunk)

    # Play the audio file
    while data:
        stream.write(data)
        default_stream.write(data)
        data = wf.readframes(chunk)

    # Stop stream
    stream.stop_stream()
    default_stream.stop_stream()
    stream.close()
    default_stream.close()

    # Close PyAudio
    p.terminate()

    # Close the audio file
    wf.close()



if __name__ == "__main__":
    audio_file_path = 'C:\\colman\\cyber\\Deceptify\\Server\\AudioFiles\\Hello world.wav'  # Replace with your audio file path
    play_audio_through_vbcable(audio_file_path)
