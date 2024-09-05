import json
from typing import Optional, Set, List

from app.Server import Util
from app.Server.data.prompt import Prompt


class Profile:
    def __init__(self, profile_name: str, audio_data_path: str) -> None:
        """
        Initialize a Profile object.

        Args:
            profile_name (str): Name of the profile.
            audio_data_path (str): Path to the audio file.
        """
        self.profile_name: str = profile_name
        self.audio_data_path: str = audio_data_path

    def getName(self) -> str:
        """
        Get the name of the profile.

        Returns:
            str: The name of the profile.
        """
        return self.profile_name

    def get_audio_data(self):
        """
        Get the path to the profile audio data.

        :returns: The path to the profile audio data.
        """
        return self.audio_data_path

    def __repr__(self) -> str:
        """
        Return a string representation of the profile.

        Returns:
            str: The string representation of the profile.
        """
        return f"Profile: {self.profile_name}, {self.audio_data_path}"

    def to_dict(self) -> dict:
        """
        Convert the profile to a dictionary.

        Returns:
            dict: A dictionary representation of the profile.
        """
        return {
            "profile_name": self.profile_name,
            "data": self.audio_data_path,
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
            json_profile["data_path"],
        )
