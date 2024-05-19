import json
from data.Profile import Profile


class AttackFactory:
    """
    A factory class for creating attack objects based on the specified attack type.
    """

    @staticmethod
    def create_attack(
        attack_type: str,
        campaign_name: str,
        mimic_profile: Profile,
        target: Profile,
        description: str,
        attack_id: int,
        recordings=None,
        transcript=None,
    ):
        """
        Create an attack object based on the specified attack type.

        Parameters:
        - attack_type (str): The type of attack. Allowed values are 'voice' and 'video'.
        - campaign_name (str): The name of the campaign.
        - mimic_profile (Profile): The profile of the attacker.
        - target (Profile): The profile of the target.
        - description (str): A description of the attack.
        - camp_id (int): The ID of the campaign.
        - recordings (list, optional): A list of recordings for the attack. Defaults to None.
        - transcript (str, optional): The transcript of the attack. Defaults to None.

        Returns:
        - Attack: An instance of the appropriate attack class based on the attack type.

        Raises:
        - ValueError: If the attack_type is not one of the allowed values.
        """
        allowed_attack_types = [
            "Voice",
            "Video",
        ]  # Define your allowed attack types here
        if attack_type == "Voice":
            return VoiceAttack(
                campaign_name,
                mimic_profile,
                target,
                description,
                attack_id,
                recordings,
                transcript,
            )
        if attack_type == "Video":
            return VideoAttack(
                campaign_name,
                mimic_profile,
                target,
                description,
                attack_id,
                recordings,
                transcript,
            )
        else:
            raise ValueError(
                f"Invalid attack_type. Allowed values are {allowed_attack_types} i got {attack_type}"
            )


class Attack:
    """
    Base class for all attack types.
    """

    def __init__(self, campaign_name, mimic_profile, target, description, camp_id):
        self.campaign_name = campaign_name
        self.mimic_profile = mimic_profile
        self.target = target
        self.description = description
        self.id = camp_id

    def get_target(self) -> Profile:
        return self.target

    def get_mimic_profile(self) -> Profile:
        return self.mimic_profile

    def getID(self):
        return self.id

    def get_role(self, profile) -> str:
        """
        Determines the role of a given profile.

        Args:
            profile (str): The profile to determine the role for.

        Returns:
            str: The role of the profile. Possible values are "Attacker" or "Victim".
        """
        if Profile == self.mimic_profile:
            return "Attacker"
        elif profile == self.target:
            return "Victim"

    def to_dict(self):
        """
        Convert the attack object to a dictionary.

        Returns:
        - dict: A dictionary representation of the attack object.
        """
        return {
            "campaign_name": self.campaign_name,
            "mimic_profile": self.mimic_profile,
            "target": self.target,
            "description": self.description,
            "id": self.id,
        }

    def to_json(self):
        """
        Convert the attack object to a JSON string.

        Returns:
        - str: A JSON string representation of the attack object.
        """
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(data):
        """
        Create an attack object from a dictionary.

        Parameters:
        - data (dict): A dictionary containing the attack data.

        Returns:
        - Attack: An instance of the Attack class created from the dictionary.
        """
        campaign_name = data["campaign_name"]
        mimic_profile = data["mimic_profile"]
        target = data["target"]
        description = data["description"]
        camp_id = data["id"]
        return Attack(campaign_name, mimic_profile, target, description, camp_id)

    @staticmethod
    def from_json(json_data):
        """
        Create an attack object from a JSON string.

        Parameters:
        - json_data (str): A JSON string containing the attack data.

        Returns:
        - Attack: An instance of the Attack class created from the JSON string.
        """
        return Attack.from_dict(json.loads(json_data))

    def __hash__(self):
        return hash(
            (
                self.campaign_name,
                self.mimic_profile,
                self.target,
                self.description,
                self.id,
            )
        )

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (
            self.campaign_name,
            self.mimic_profile,
            self.target,
            self.description,
            self.id,
        ) == (other.campaign_name, other.mimic_profile, other.target, other.description)


# TODO: CONTINUE THIS VOICEATTACK IMPLEMENTATION.
class VoiceAttack(Attack):
    """
    Class representing a voice attack.
    """

    def __init__(
        self,
        campaign_name,
        mimic_profile,
        target,
        description,
        camp_id,
        recordings,
        transcript=None,
    ):
        super().__init__(campaign_name, mimic_profile, target, description, camp_id)
        self.recordings = recordings
        self.transcript = transcript

    def to_dict(self):
        super_dict = super().to_dict()
        super_dict["recordings"] = self.recordings
        if self.transcript:
            super_dict["transcript"] = self.transcript
        return super_dict

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(data):
        campaign_name = data["campaign_name"]
        mimic_profile = data["mimic_profile"]
        target = data["target"]
        description = data["description"]
        camp_id = data["id"]
        recordings = data["recordings"]
        transcript = data["transcript"]
        return VoiceAttack(
            campaign_name,
            mimic_profile,
            target,
            description,
            camp_id,
            recordings,
            transcript,
        )

    @staticmethod
    def from_json(json_data):
        return VoiceAttack.from_dict(json.loads(json_data))

    def __hash__(self):
        return hash(
            (
                self.campaign_name,
                self.mimic_profile,
                self.target,
                self.description,
                self.id,
                self.recordings,
                self.transcript,
            )
        )

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (
            self.campaign_name,
            self.mimic_profile,
            self.target,
            self.description,
            self.id,
            self.transcript,
            self.recordings,
        ) == (
            other.campaign_name,
            other.mimic_profile,
            other.target,
            other.description,
            other.transcript,
            other.recordings,
        )


# TODO: CONTINUE THIS VIDEOATTACK IMPLEMENTATION.
class VideoAttack(Attack):
    """
    Class representing a video attack.
    """

    def __init__(
        self,
        campaign_name,
        mimic_profile,
        target,
        description,
        camp_id,
        video_recordings,
        transcript=None,
    ):
        super().__init__(campaign_name, mimic_profile, target, description, camp_id)
        self.video_recordings = video_recordings
        self.transcript = transcript

    def to_dict(self):
        super_dict = super().to_dict()
        super_dict["recordings"] = self.video_recordings
        if self.transcript:
            super_dict["transcript"] = self.transcript
        return super_dict

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(data):
        campaign_name = data["campaign_name"]
        mimic_profile = data["mimic_profile"]
        target = data["target"]
        description = data["description"]
        camp_id = data["id"]
        recordings = data["recordings"]
        transcript = data["transcript"]
        return VideoAttack(
            campaign_name,
            mimic_profile,
            target,
            description,
            camp_id,
            recordings,
            transcript,
        )

    @staticmethod
    def from_json(json_data):
        return VideoAttack.from_dict(json.loads(json_data))

    def __hash__(self):
        return hash(
            (
                self.campaign_name,
                self.mimic_profile,
                self.target,
                self.description,
                self.id,
                self.video_recordings,
                self.transcript,
            )
        )

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (
            self.campaign_name,
            self.mimic_profile,
            self.target,
            self.description,
            self.id,
            self.transcript,
            self.video_recordings,
        ) == (
            other.campaign_name,
            other.mimic_profile,
            other.target,
            other.description,
            other.transcript,
            other.video_recordings,
        )
