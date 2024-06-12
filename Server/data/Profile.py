import base64
import json
from flask import session, current_app as app
from typing import Optional, Set, Union, List

from Server import Util
from Server.data.prompt import Prompt


class Profile:
    def __init__(self, profile_name: str, general_info: str, data_path: str) -> None:
        """
        Initialize a Profile object.

        Args:
            profile_name (str): Name of the profile.
            general_info (str): Some description about the profile.
            data_path (str): Path to the data file.
        """
        self.profile_name: str = profile_name
        self.general_info: str = general_info
        self.Attacks: List = list()
        self.prompts: Set[Prompt] = set()
        self.data_path: str = data_path
        self.setDefaultPrompts()

        # Create a voice profile on the server
        Util.createvoice_profile("gur", profile_name, data_path)

        # Generate voice for each default prompt
        for prompt in self.prompts:
            with open("AudioFiles/" + prompt.filename, "wb") as f:
                f.write(Util.generate_voice("gur", self.profile_name, prompt.prompt_desc))



    def getName(self) -> str:
        """
        Get the name of the profile.

        Returns:
            str: The name of the profile.
        """
        return self.profile_name

    def get_data(self):
        """
        Get the path to the profile data.

        :returns: The path to the profile data.
        """
        return self.data_path

    def getGeneralInfo(self) -> str:
        """
        Get the general information of the profile.

        Returns:
            str: The general information of the profile.
        """
        return self.general_info

    def addAttack(self, attack) -> None:
        """
        Add an attack to the profile.

        Args:
            attack: The attack to be added.
        """
        # self.Attacks.add(attack)
        print("addAttack->Profile")
        print({**attack.to_dict(), "role": attack.get_role(self)})
        # self.Attacks.add(attack.to_dict().update({"role": attack.get_role(self)}))
        self.Attacks.append({**attack.to_dict(), "role": attack.get_role(self)})

    def getPrompt(self, prompt_desc: str) -> Optional[Prompt]:
        """
        Get a specific prompt by its description.

        Args:
            prompt_desc (str): The description of the prompt.

        Returns:
            Optional[Prompt]: The prompt object if found, None otherwise.
        """
        for p in self.prompts:
            if p.prompt_desc == prompt_desc:
                return p
        return None

    def getPrompts(self) -> Set[Prompt]:
        """
        Get all prompts of the profile.

        Returns:
            Set[Prompt]: A set of all prompts.
        """
        return self.prompts

    def addPrompt(self, prompt: Prompt) -> None:
        """
        Add a prompt to the profile.

        Args:
            prompt (Prompt): The prompt to be added.
        """
        self.prompts.add(prompt)

    def setDefaultPrompts(self) -> None:
        """
        Set default prompts for the profile.
        """
        default_prompts = [
            "Hello", "Hi", "Thank you", "Bye", "Sorry", "Why",
            "What did you say", "I dont know", "What are you talking about",
            "What", "Yes", "No"
        ]
        for prompt_desc in default_prompts:
            self.addPrompt(Prompt(prompt_desc=prompt_desc, is_deletable=False))

    def deletePrompt(self, desc: str) -> None:
        """
        Delete a prompt from the profile by its description.

        Args:
            desc (str): The description of the prompt to be deleted.
        """
        prompt_to_remove = None
        for prt in self.prompts:
            if prt.prompt_desc == desc:
                prompt_to_remove = prt
                break
        if prompt_to_remove:
            self.prompts.remove(prompt_to_remove)

    def __repr__(self) -> str:
        """
        Return a string representation of the profile.

        Returns:
            str: The string representation of the profile.
        """
        return f"Profile: {self.profile_name}, {self.general_info}, {self.data_path}, {self.get_attacks()}"

    def get_attacks(self) -> List:
        """
        Get all attacks associated with the profile.

        Returns:
            Set: A set of all attacks.
        """
        # return self.AttackerAttacks.union(self.victimAttacks)
        return self.Attacks

    def to_dict(self) -> dict:
        """
        Convert the profile to a dictionary.

        Returns:
            dict: A dictionary representation of the profile.
        """
        return {
            "profile_name": self.profile_name,
            "general_info": self.general_info,
            "data": self.data_path,
        }

    def to_json(self) -> str:
        """
        Convert the profile to a JSON string for future transmission.

        Returns:
            str: A JSON string representation of the profile.
        """
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_profile: str) -> 'Profile':
        """
        Create a Profile object from a JSON string.

        Args:
            json_profile (str): The JSON string representing a profile.

        Returns:
            Profile: The created Profile object.
        """
        profile_dict = json.loads(json_profile)
        return Profile.from_dict(profile_dict)

    @staticmethod
    def from_dict(json_profile: dict) -> 'Profile':
        """
        Create a Profile object from a dictionary.

        Args:
            json_profile (dict): The dictionary representing a profile.

        Returns:
            Profile: The created Profile object.
        """
        return Profile(
            json_profile["profile_name"],
            json_profile["general_info"],
            json_profile["data_path"],
        )
