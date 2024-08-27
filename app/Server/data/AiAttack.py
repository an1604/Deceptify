import json
from profile import Profile
from datetime import datetime


class AiAttack:
    """
    Base class for all attack types.
    """

    def __init__(self, campaign_name, target_name, message_type, message_name, attack_purpose,
                 place, attack_id, is_success = None):
        self.campaign_name = campaign_name
        self.target_name = target_name
        self.message_type = message_type
        self.message_name = message_name
        self.attack_purpose = attack_purpose
        self.place = place
        self.attack_id = attack_id
        self.recording = None
        self.transcript = None
        self.is_success = is_success

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

    def getResult(self):
        return self.is_success

    def setResult(self, result):
        self.is_success = result

    def get_attack_prompts(self) -> set[str]:
        if self.attack_purpose == "Bank":
            return {"We had a suspicious activity in your account and we need verification to make action",
                    "We detected some suspicious transactions",
                    "In order to continue further i need your account number",
                    "It is to confirm your identity", "Yes after we verify your identity", "Wait a second umm",
                    "Hold on a second umm", "I need your account number", "Can you repeat that",
                    "Let me check umm", "Goodbye", "This is not a real number",
                    "Thank you, we have solved the issue. Goodbye", "I need a 6 digit account number"}
        elif self.attack_purpose == "Delivery":
            return {"We have your package and we need your address to send it", "we do not have that information",
                    "We need it to know where to send the package", "It is not provided in the package",
                    "Yes to ensure it’s delivered correctly", "It was on the shipping label", "Wait a second umm",
                    "Hold on a second umm", "I need your address", "Let me check umm", "Can you repeat that",
                    "Goodbye"}
        else:  # self.attack_purpose == "Hospital":
            return {"We had an attack on our system and we need your ID to solve this issue",
                    "There has been an attempt of a personal data theft",
                    "I need your ID to reopen your account", "Your ID is the only way to open your account",
                    "Wait a second umm", "Hold on a second umm", "Let me check umm", "Can you repeat that",
                    "Goodbye", "This is not a real number", "Thank you, we have opened your account. Goodbye",
                    "I need a 9 digit ID"}

    def setRec(self, path):
        self.recording = path

    def setTranscript(self, path):
        self.transcript = path

    def to_dict(self):
        """
        Convert the attack object to a dictionary.

        Returns:
        - dict: A dictionary representation of the attack object.
        """
        return {
            "campaign_name": self.campaign_name,
            "target_name": self.target_name,
            "message_type": self.message_type,
            "message_name": self.message_name,
            "attack_purpose": self.attack_purpose,
            "place": self.place,
            "attack_id": self.attack_id,
            "recording": self.recording,
            "transcript": self.transcript,
            "is_success": self.is_success
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
        target_name = data["target_name"]
        message_type = data["message_type"]
        message_name = data["message_name"]
        attack_purpose = data["attack_purpose"]
        place = data["place"]
        attack_id = data["attack_id"]
        is_success = data["is_success"]
        return AiAttack(campaign_name, target_name, message_type, message_name, attack_purpose,
                        place, attack_id, is_success)

    @staticmethod
    def from_json(json_data):
        """
        Create an attack object from a JSON string.

        Parameters:
        - json_data (str): A JSON string containing the attack data.

        Returns:
        - Attack: An instance of the Attack class created from the JSON string.
        """
        return AiAttack.from_dict(json.loads(json_data))

    def __hash__(self):
        return hash(
            (
                self.campaign_name,
                self.target_name,
                self.message_type,
                self.message_name,
                self.attack_purpose,
                self.place,
                self.attack_id,
                self.is_success
            )
        )

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (
            self.campaign_name,
            self.target_name,
            self.message_type,
            self.message_name,
            self.attack_purpose,
            self.place,
            self.attack_id,
        ) == (other.campaign_name, other.target_name, other.message_type, other.message_name,
              other.attack_purpose, other.place, other.attack_id)
