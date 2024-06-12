import soundcard as sc
import numpy as np
import wave

SAMPLE_RATE = 44100
RECORD_SECONDS = 60
OUTPUT_FILENAME = "output.wav"

mic = sc.default_microphone()
speaker = sc.default_speaker()

mic_frames = []
speaker_frames = []

with mic.recorder(samplerate=SAMPLE_RATE) as mic_recorder, speaker.recorder(
    samplerate=SAMPLE_RATE
) as speaker_recorder:
    print("Recording...")
    for _ in range(int(SAMPLE_RATE / 1024 * RECORD_SECONDS)):
        mic_data = mic_recorder.record(numframes=1024)
        speaker_data = speaker_recorder.record(numframes=1024)
        mic_frames.append(mic_data)
        speaker_frames.append(speaker_data)
    print("Finished recording.")

# Combine mic and speaker data
combined_frames = np.array(mic_frames) + np.array(speaker_frames)

# Save the recorded data
combined_frames = np.array(combined_frames * 32767, dtype=np.int16)
with wave.open(OUTPUT_FILENAME, "w") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(combined_frames.tobytes())
