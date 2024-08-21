import json
from profile import Profile
from datetime import datetime


class AttackFactory:
    """
    A factory class for creating attack objects based on the specified attack type.
    """

    @staticmethod
    def create_attack(
            attack_type: str,
            campaign_name: str,
            target_name: str,
            message_type: str,
            message_name: str,
            attack_purpose: str,
            place: str,
            attack_id: int,
            recording=None,
            transcript=None,
    ):
        """
        Create an attack object based on the specified attack type.

        Parameters:
        - attack_type (str): The type of attack. Allowed values are 'AI' and 'Clone'.
        - campaign_name (str): The name of the campaign.
        # - mimic_profile (Profile): The profile of the attacker.
        # - target (Profile): The profile of the target.
        # - description (str): A description of the attack.
        - target_name (str): The name of the target.
        - message_type (str): The type of message (whatsapp or email).
        - message_name (str): The name of the recipient.
        - attack_purpose (str): The purpose of the attack.
        - place (str): The name of the place the attacker is imposing to be from.
        - attack_id (int): The ID of the attack.
        - recordings (list, optional): A list of recordings for the attack. Defaults to None.
        - transcript (str, optional): The transcript of the attack. Defaults to None.

        Returns:
        - Attack: An instance of the appropriate attack class based on the attack type.

        Raises:
        - ValueError: If the attack_type is not one of the allowed values.
        """
        allowed_attack_types = [
            "AI",
            "Clone",
        ]  # Define your allowed attack types here
        if attack_type == "AI":
            return AiAttack(
                attack_type,
                campaign_name,
                target_name,
                message_type,
                message_name,
                attack_purpose,
                place,
                attack_id,
                recording,
                transcript,
            )
        # if attack_type == "Clone":
        #    return CloneAttack(
        #        campaign_name,
        #        mimic_profile,
        #        target,
        #        description,
        #        attack_purpose,
        #        attack_id,
        #        recording,
        #        transcript,
        #    )
        else:
            raise ValueError(
                f"Invalid attack_type. Allowed values are {allowed_attack_types} i got {attack_type}"
            )


class Attack:
    """
    Base class for all attack types.
    """

    def __init__(self, attack_type, campaign_name, target_name, message_type, message_name, attack_purpose,
                 place, attack_id):
        self.attack_type = attack_type
        self.campaign_name = campaign_name
        self.target_name = target_name
        self.message_type = message_type
        self.message_name = message_name
        self.attack_purpose = attack_purpose
        self.place = place
        self.attack_id = attack_id
        self.recording = None
        self.transcript = None
        self.setRec()
        self.setTranscript()

    def getType(self) -> str:
        return self.attack_type

    def getName(self) -> str:
        return self.campaign_name

    def getTargetName(self) -> str:
        return self.target_name

    def getMessageType(self) -> str:
        return self.message_type

    def getMessageName(self) -> str:
        return self.message_name

    def getPurpose(self):
        return self.attack_purpose

    def getID(self):
        return self.attack_id

    def getPlace(self):
        return self.place

    def getRec(self):
        return self.recording

    def getTranscript(self):
        return self.transcript

    def get_attack_prompts(self) -> set[str]:
        if self.attack_purpose == "Bank":
            return {"We had a suspicious activity in your account and we need verification to make action",
                    "We detected some suspicious transactions",
                    "In order to continue further i need your account number",
                    "It is to confirm your identity", "Yes after we verify your identity", "Wait a second Umm",
                    "Hold on a second Umm", "I need your account number", "Can you repeat that",
                    "Let me check umm"}
        elif self.attack_purpose == "Delivery":
            return {"We have your package and we need your address to send it", "we do not have that information",
                    "We need it to know where to send the package", "It is not provided in the package",
                    "Yes to ensure it’s delivered correctly", "It was on the shipping label", "Wait a second Umm",
                    "Hold on a second Umm", "I need your address", "Let me check umm", "Can you repeat that"}
        elif self.attack_purpose == "Hospital":
            return {"We had an attack on our system and we need your ID to solve this issue",
                    "There has been an attempt of a personal data theft",
                    "I need your ID to reopen your account", "Your ID is the only way to open your account",
                    "Wait a second Umm", "Hold on a second Umm", "Let me check umm", "Can you repeat that"}
        else:  # self.attack_purpose == "whatsapp"
            return {"We had a suspicious activity in your account and we need verification to make action",
                    "We detected some suspicious transactions", "In order to continue further i need your ID",
                    "It is to confirm your identity", "Yes after we verify your identity", "Wait a second Umm",
                    "Hold on a second Umm", "I need your ID and account number",
                    "Let me check umm"}

    def setRec(self):
        self.recording = (self.target_name + "-" + self.attack_purpose + "-" +
                          datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".wav")

    def setTranscript(self):
        self.transcript = (self.target_name + "-" + self.attack_purpose + "-" +
                           datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json")

    def to_dict(self):
        """
        Convert the attack object to a dictionary.

        Returns:
        - dict: A dictionary representation of the attack object.
        """
        return {
            "attack_type": self.attack_type,
            "campaign_name": self.campaign_name,
            "target_name": self.target_name,
            "message_type": self.message_type,
            "message_name": self.message_name,
            "attack_purpose": self.attack_purpose,
            "place": self.place,
            "attack_id": self.attack_id,
            "recording": self.recording,
            "transcript": self.transcript,
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
        attack_type = data["attack_type"]
        campaign_name = data["campaign_name"]
        target_name = data["target_name"]
        message_type = data["message_type"]
        message_name = data["message_name"]
        attack_purpose = data["attack_purpose"]
        place = data["place"]
        attack_id = data["attack_id"]
        return Attack(attack_type, campaign_name, target_name, message_type, message_name, attack_purpose,
                      place, attack_id)

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
                self.attack_type,
                self.campaign_name,
                self.target_name,
                self.message_type,
                self.message_name,
                self.attack_purpose,
                self.place,
                self.attack_id,
            )
        )

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (
            self.attack_type,
            self.campaign_name,
            self.target_name,
            self.message_type,
            self.message_name,
            self.attack_purpose,
            self.place,
            self.attack_id,
        ) == (other.attack_type, other.campaign_name, other.target_name, other.message_type, other.message_name,
              other.attack_purpose, other.place, other.attack_id)


class AiAttack(Attack):
    """
    Class representing a voice attack.
    """

    def __init__(
            self,
            attack_type,
            campaign_name,
            target_name,
            message_type,
            message_name,
            attack_purpose,
            place,
            attack_id,
            recording=None,
            transcript=None,
    ):
        super().__init__(attack_type, campaign_name, target_name, message_type, message_name,
                         attack_purpose, place, attack_id)

    def to_dict(self):
        super_dict = super().to_dict()
        if self.recording:
            super_dict["recording"] = self.recording
        if self.transcript:
            super_dict["transcript"] = self.transcript
        return super_dict

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(data):
        attack_type = data["attack_type"]
        campaign_name = data["campaign_name"]
        target_name = data["target_name"]
        message_type = data["message_type"]
        message_name = data["message_name"]
        attack_purpose = data["attack_purpose"]
        place = data["place"]
        attack_id = data["attack_id"]
        return AiAttack(attack_type, campaign_name, target_name, message_type, message_name, attack_purpose,
                        place, attack_id)

    @staticmethod
    def from_json(json_data):
        return AiAttack.from_dict(json.loads(json_data))

    def __hash__(self):
        return hash(
            (
                self.attack_type,
                self.campaign_name,
                self.target_name,
                self.message_type,
                self.message_name,
                self.attack_purpose,
                self.place,
                self.attack_id,
            )
        )

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (
            self.attack_type,
            self.campaign_name,
            self.target_name,
            self.message_type,
            self.message_name,
            self.attack_purpose,
            self.place,
            self.attack_id,
        ) == (other.attack_type, other.campaign_name, other.target_name, other.message_type, other.message_name,
              other.attack_purpose, other.place, other.attack_id)


"""
class CloneAttack(Attack):
    # Class representing a video attack.

    def __init__(
            self,
            campaign_name,
            mimic_profile,
            target,
            description,
            attack_purpose,
            attack_id,
            voice_type,
            place,
            video_recordings=None,
            transcript=None,
    ):
        super().__init__(campaign_name, mimic_profile, target, description, attack_purpose, attack_id, voice_type, place)
        self.video_recordings = video_recordings
        self.transcript = transcript

    def to_dict(self):
        super_dict = super().to_dict()
        if self.video_recordings:
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
        attack_purpose = data["purpose"]
        attack_id = data["attack_id"]
        voice_type = data["voice_type"]
        place = data["place"]
        recordings = data["recordings"]
        transcript = data["transcript"]
        return CloneAttack(
            campaign_name,
            mimic_profile,
            target,
            description,
            attack_purpose,
            attack_id,
            voice_type,
            place,
            recordings,
            transcript,
        )

    @staticmethod
    def from_json(json_data):
        return CloneAttack.from_dict(json.loads(json_data))

    def __hash__(self):
        return hash(
            (
                self.campaign_name,
                self.mimic_profile,
                self.target,
                self.description,
                self.attack_purpose,
                self.attack_id,
                self.voice_type,
                self.place,
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
            self.attack_purpose,
            self.attack_id,
            self.voice_type,
            self.place,
            self.transcript,
            self.video_recordings,
        ) == (
            other.campaign_name,
            other.mimic_profile,
            other.target,
            other.description,
            other.attack_purpose,
            other.attack_id,
            other.voice_type,
            other.place,
            other.transcript,
            other.video_recordings,
        )
"""
