import base64
import json
import os
from flask import session, current_app as app


class Prompt:
    def __init__(self, prompt_desc,is_deletable=True):
        """
        :param prompt_desc: the prompt description
        :param prompt_profile: the profile that is connected to the prompt
        :param data: the recording of the prompt
        """

        self.prompt_desc = prompt_desc
        #self.prompt_profile = prompt_profile
        #self.audio_path = os.path.join(app.config['UPLOAD_FOLDER'], "Test.mp3")
        self.filename = "Test.mp3"
        self.is_deletable = is_deletable

    def __repr__(self):
        return f"Prompt: {self.prompt_desc}"

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
