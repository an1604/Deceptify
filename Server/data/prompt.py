import base64
import json
import os
from flask import session, current_app as app

# TODO: fix when saving to pkl file and getting from pkl file
class Prompt:
    def __init__(self, prompt_desc, prompt_profile, is_video=False, is_deletable=True):
        """
        :param prompt_desc: the prompt description
        :param prompt_profile: the profile that is connected to the prompt
        :param is_deletable: whether the prompt is deletable
        """

        self.prompt_desc = prompt_desc
        self.prompt_profile = prompt_profile
        # self.audio_path = os.path.join(app.config['UPLOAD_FOLDER'], "Test.mp3")
        self.filename = prompt_profile + "-" + prompt_desc + ".wav"
        self.videoname = prompt_profile + "-" + prompt_desc + ".mp4"
        self.defaultvid = prompt_profile + ".mp4"
        self.is_deletable = is_deletable
        self.is_video = is_video

    def __repr__(self):
        return (f"Prompt: {self.prompt_desc}, {self.prompt_profile}, {self.filename}, {self.videoname},"
                f" {self.defaultvid}, {self.is_deletable}, {self.is_video}")

    def to_dict(self):
        return {
            "prompt_desc": self.prompt_desc,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_prompt): return json.loads(json_prompt)

    @staticmethod
    def from_dict(json_prompt):
        return Prompt(json_prompt["prompt_desc"])
