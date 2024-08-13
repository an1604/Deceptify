import os

from transformers import BarkModel, AutoProcessor
import torch
import scipy

bark = BarkModel.from_pretrained("suno/bark-small")
device = "cuda:0" if torch.cuda.is_available() else "cpu"
bark = bark.to(device)
processor = AutoProcessor.from_pretrained("suno/bark")
voice_preset = "v2/en_speaker_6"


def generateSpeech(text_prompt, path):
    inputs = processor(text_prompt, voice_preset=voice_preset)
    speech_output = bark.generate(**inputs.to(device))
    sampling_rate = bark.generation_config.sample_rate
    scipy.io.wavfile.write(path, rate=sampling_rate, data=speech_output[0].cpu().numpy())


if __name__ == '__main__':
    generateSpeech("Goodbye", os.getcwd() + "\\audio.wav")
