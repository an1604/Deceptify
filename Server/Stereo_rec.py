import pyaudio
import wave


def get_stereo_mix_index(p):
    for i in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(i)
        if "Stereo Mix" in dev_info.get('name', ''):
            print(f"Found Stereo Mix at index {i}: {dev_info['name']}")
            return i
    return None


def record_from_stereo_mix(output_filename, duration=10, sample_rate=44100, chunk_size=1024):
    p = pyaudio.PyAudio()
    stereo_mix_index = get_stereo_mix_index(p)

    if stereo_mix_index is None:
        print("Stereo Mix not found.")
        return

    stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=sample_rate,
                    input=True,
                    input_device_index=stereo_mix_index,
                    frames_per_buffer=chunk_size)

    print("Recording...")
    frames = []

    for _ in range(int(sample_rate / chunk_size * duration)):
        data = stream.read(chunk_size)
        frames.append(data)

    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

    print(f"Audio saved as {output_filename}")


if __name__ == "__main__":
    record_from_stereo_mix(output_filename="output.wav", duration=10)
