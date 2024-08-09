"""
To run bark in this case, run the following commands before running this script:
    `pip install -r requirements.txt`
    `git lfs install`
    `git clone https://huggingface.co/suno/bark-small`
"""


from TTS.tts.configs.bark_config import BarkConfig
from TTS.tts.models.bark import Bark
import scipy

config = BarkConfig()
model = Bark.init_from_config(config)
model.load_checkpoint(config, checkpoint_dir="bark/", eval=True)

text = "Subscribe to my channel for more videos!"
# with random speaker
output_dict = model.synthesize(text, config, speaker_id="random", voice_dirs=None)
# output_dict = model.synthesize(text, config, speaker_id="speaker", voice_dirs="bark_voices/")

# write the file to disk
# Save the .wav file into the disk
sample_rate = 24000  # model.generation_config.sample_rate
scipy.io.wavfile.write("bark_out.wav", rate=sample_rate, data=output_dict["wav"])
