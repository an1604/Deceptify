import requests
import numpy as np
import json


def send_speech_generation_request(text, speaker_wav_np_array, profile_name,
                                   server_url='http://localhost:8080/generate_speech'):
    """Send a request to the Flask server to generate speech from text and a speaker WAV sample."""

    # Convert the NumPy array to a list to make it JSON serializable
    speaker_wav_list = speaker_wav_np_array.tolist()

    # Prepare the data payload
    payload = {
        'text': text,
        'speaker_wav': speaker_wav_list,
        'profile_name': profile_name
    }

    # Send the POST request to the server
    try:
        response = requests.post(server_url, json=payload)

        # Check for a successful request
        if response.status_code == 200:
            # If successful, save the received audio file
            with open(f"{profile_name}_generated.wav", 'wb') as f:
                f.write(response.content)
            print("Audio file received and saved.")
        else:
            # If there was an error, print the error message
            print(f"Error: {response.status_code}, {response.json()}")

    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage:
if __name__ == "__main__":
    # Example text and profile name
    text = "Hello, this is a generated speech."
    profile_name = "example_profile"

    # Example NumPy array representing the WAV file data
    # For the sake of this example, we'll generate a simple sine wave signal
    import numpy as np
    import scipy.io.wavfile as wav

    sample_rate = 44100
    t = np.linspace(0., 1., sample_rate)
    speaker_wav_np_array = 0.5 * np.sin(2. * np.pi * 440. * t)  # Simple 440Hz sine wave

    # Send the request
    send_speech_generation_request(text, speaker_wav_np_array, profile_name)
