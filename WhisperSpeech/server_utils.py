import os

import numpy as np
from scipy.io.wavfile import write

import string


def create_directory_if_not_exists(directory_path):
    """Create a directory if it does not exist."""
    try:
        os.makedirs(directory_path, exist_ok=True)
    except Exception as e:
        print(f"Failed to create directory {directory_path}: {e}")
        raise


def save_speaker_wav_to_dir(speaker_wav_obj, save_wav_path, rate=44100):
    """Save a NumPy array as a WAV file."""
    try:
        scaled = np.int16(speaker_wav_obj / np.max(np.abs(speaker_wav_obj)) * 32767)
        write(save_wav_path, rate, scaled)
        print(f"Wave file saved at {save_wav_path}")
    except Exception as e:
        print(f"Failed to save WAV file: {e}")
        raise


def clean_text(text):
    text = text.replace(" ", "_")
    text = text.translate(str.maketrans('', '', string.punctuation))
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    text = ''.join(c for c in text if c in valid_chars)
    return text.lower()
