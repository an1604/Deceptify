import pytest
import os

import pyaudio
import wave


def record_audio(duration=5, output_filename='files/output_test.wav'):
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    p = pyaudio.PyAudio()

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []
    for _ in range(0, int(fs / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()


def play_audio(input_filename='files/output_test.wav'):
    chunk = 1024
    wf = wave.open(input_filename, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()


def test_record_audio():
    output_file = 'files/test_output.wav'
    duration = 2  # Record 2 seconds for testing
    record_audio(duration=duration, output_filename=output_file)

    assert os.path.exists(output_file)

    file_size = os.path.getsize(output_file)
    assert file_size > 0, "Recorded file is empty."


def test_play_audio():
    input_file = 'files/test.wav'
    try:
        play_audio(input_filename=input_file)
        assert True, "Audio played successfully."
    except Exception as e:
        pytest.fail(f"Audio playback failed with error: {e}")
    os.remove(input_file)


def test_audio_input_output_cable():
    input_file = 'test_output.wav'

    record_audio(duration=1, output_filename=input_file)
    play_audio(input_filename=input_file)

    # Assert that the input file was created and has data
    assert os.path.exists(input_file), "Recorded file does not exist."
    assert os.path.getsize(input_file) > 0, "Recorded file is empty."

    os.remove(input_file)

