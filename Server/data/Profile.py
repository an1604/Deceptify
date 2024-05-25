import base64
import json
from flask import session, current_app as app

from Server.data.prompt import Prompt

class Profile:
    def __init__(self, profile_name, role, data_type,general_info, data):
        """
        :param profile_name: name of the profile
        :param role: role of the profile
        :param data_type: Dataset, record, video or image.
        :param general_info: some description about the profile.
        :param data: the actual data of the profile for training.
        """
        self.profile_name = profile_name
        self.role = role
        self.data_type = data_type
        self.general_info = general_info
        self.victimAttacks = set()
        self.AttackerAttacks = set()
        self.prompts = set[Prompt]()
        self.data = base64.b64encode(data.read()).decode('utf-8')  # embedd the data to make it JSON serializable.
        self.setDefaultPrompts()

    def getName(self) -> str:
        return self.profile_name

    def getRole(self) -> str:
        return self.role

    def getGeneralInfo(self) -> str:
        return self.general_info

    def addAttack(self, attack) -> None:
        if attack.get_role(self) == "Attacker":
            self.AttackerAttacks.add(attack)
        else:
            self.victimAttacks.add(attack)

    def getPrompt(self, prompt_desc) -> Prompt | None:
        for p in self.prompts:
            if p.prompt_desc == prompt_desc:
                return p
        return None

    def getPrompts(self) -> set[Prompt]:
        return self.prompts

    def addPrompt(self, prompt) -> None:
        self.prompts.add(prompt)

    def setDefaultPrompts(self) -> None:
        self.addPrompt(Prompt(prompt_desc="Hello", is_deletable=False))
        self.addPrompt(Prompt(prompt_desc="Hi", is_deletable=False))
        self.addPrompt(Prompt(prompt_desc="Thank you", is_deletable=False))
        self.addPrompt(Prompt(prompt_desc="Bye", is_deletable=False))
        self.addPrompt(Prompt(prompt_desc="Sorry", is_deletable=False))
        self.addPrompt(Prompt(prompt_desc="Why?", is_deletable=False))
        self.addPrompt(Prompt(prompt_desc="What did you say?", is_deletable=False))
        self.addPrompt(Prompt(prompt_desc="I don't know", is_deletable=False))
        self.addPrompt(Prompt(prompt_desc="what are you talking about", is_deletable=False))

    def deletePrompt(self, desc) -> None:
        prompt = None
        for prt in self.prompts:
            if prt.prompt_desc == desc:
                prompt = prt
        self.prompts.remove(prompt)

    def __repr__(self):
        return f"Profile: {self.profile_name}, {self.role}, {self.data_type}, {self.general_info}, {self.data}, {self.get_attacks()}"

    def get_attacks(self):
        return self.AttackerAttacks.union(self.victimAttacks)

    def to_dict(self):
        return {
            "profile_name": self.profile_name,
            "role": self.role,
            "data_type": self.data_type,
            "general_info": self.general_info,
            "data": self.data,
        }

    def to_json(
        self,
    ):  # Converting to json for future transmission (to the remote server).
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_profile):
        return json.loads(json_profile)

    @staticmethod
    def from_dict(json_profile):
        return Profile(
            json_profile["profile_name"],
            json_profile["role"],
            json_profile["data_type"],
            json_profile["general_info"],
            json_profile["data"],
        )
