import base64
import json
from flask import session, current_app as app


class Prompt:
    def __init__(self, prompt_desc):
        """
        :param prompt_desc: the prompt description
        :param prompt_profile: the profile that is connected to the prompt
        :param data: the recording of the prompt
        """

        self.prompt_desc = prompt_desc
        #self.prompt_profile = prompt_profile
        #self.data = base64.b64encode(data.read()).decode('utf-8')  # embedd the data to make it JSON serializable.
        #self.is_deletable(for premade prompts)

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
