import base64
import json
from flask import session, current_app as app


class Profile:
    def __init__(self, profile_name, role, general_info):
        """
        :param profile_name: name of the profile
        :param role: role of the profile
        :param data_type: Dataset, record, video or image.
        :param general_info: some description about the profile.
        :param data: the actual data of the profile for training.
        """
        self.profile_name = profile_name
        self.role = role
        self.general_info = general_info
        self.victimAttacks = set()
        self.AttackerAttacks = set()

    def getName(self) -> str:
        return self.profile_name

    def getRole(self) -> str:
        return self.role

    def addAttack(self, attack) -> None:
        if attack.get_role(self) == "Attacker":
            self.AttackerAttacks.add(attack)
        else:
            self.victimAttacks.add(attack)

    def __repr__(self):
        return f"Profile: {self.profile_name},{self.role},{self.general_info},{self.get_attacks()}"

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
