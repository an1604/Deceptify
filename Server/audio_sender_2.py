import sounddevice as sd
import wave
import threading
import numpy as np

CHUNK = 1024

def play_audio(file_path, event):
    try:
        wf = wave.open(file_path, 'rb')
        sample_rate = wf.getframerate()
        num_channels = wf.getnchannels()

        def callback(outdata, frames, time, status):
            if status:
                print(status)
            data = wf.readframes(frames)
            if len(data) == 0:
                event.set()
                raise sd.CallbackStop
            data = np.frombuffer(data, dtype=np.int16).reshape(-1, num_channels)

            if len(data) < frames:
                # If the read data is less than the required frames, pad with zeros
                outdata[:len(data)] = data
                outdata[len(data):] = 0
            else:
                outdata[:] = data

        with sd.OutputStream(samplerate=sample_rate, channels=num_channels, dtype='int16', callback=callback):
            event.wait()
    except Exception as e:
        print(f"Exception in play_audio: {e}")

def record_and_play(event):
    try:
        def callback(indata, outdata, frames, time, status):
            if status:
                print(status)
            outdata[:] = indata

        with sd.Stream(channels=1, dtype='int16', callback=callback):
            event.wait()
    except Exception as e:
        print(f"Exception in record_and_play: {e}")

def main():
    file_path = 'C:\\colman\\cyber\\Deceptify\\Server\\AudioFiles\\Test.wav'
    stop_event = threading.Event()

    # Start the play_audio thread
    playback_thread = threading.Thread(target=play_audio, args=(file_path, stop_event))
    playback_thread.start()

    # Start the record_and_play thread
    record_thread = threading.Thread(target=record_and_play, args=(stop_event,))
    record_thread.start()

    playback_thread.join()
    stop_event.set()
    record_thread.join()

if __name__ == '__main__':
    main()
