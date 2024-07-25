import base64
import json
import os
import pickle
from typing import Set, List, Optional, Type

from Server.data.Profile import Profile
from Server.data.Attacks import Attack


class DataStorage:
    """
    A class that represents the data storage for profiles, prompts, and attacks.
    """

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
        if not self._shared_state:
            self.profiles: Set[Profile] = set()
            self.attacks: Set = set()

    def add_profile(self, profile: Profile) -> None:
        """
        Add a profile to the data storage.

        Args:
            profile (Profile): The profile to be added.
        """
        self.profiles.add(profile)

    def add_attack(self, new_attack) -> None:
        """
        Add an attack to the data storage.
        This also adds the attack to the target and victim profiles.

        Args:
            new_attack: The attack to be added.
        """
        # target = new_attack.get_target()
        # victim = new_attack.get_mimic_profile()
        # target.addAttack(new_attack)
        # victim.addAttack(new_attack)
        self.attacks.add(new_attack)
        print(f'dataStorage attacks: {self.attacks}')

    def get_attacks(self) -> Set:
        """
        Get all the attacks stored in the data storage.

        Returns:
            Set: A set of attacks.
        """
        return self.attacks

    def delete_attack(self, attackID) -> None:
        """
        Delete an attack from the data storage.

        Args:
            attackID: The ID of the attack to be deleted.
        """
        attack_to_remove = None
        for attack in self.attacks:
            if attack.getID() == attackID:
                attack_to_remove = attack
                break
        if attack_to_remove:
            self.attacks.remove(attack_to_remove)

    def get_AllProfiles(self) -> Set[Profile]:
        """
        Get all the profiles stored in the data storage.

        Returns:
            Set[Profile]: A set of profiles.
        """
        return self.profiles

    def get_profiles(self) -> Set[Profile]:
        """
        Get the profiles stored in the data storage.

        Returns:
            Set[Profile]: A set of profiles.
        """
        return self.profiles

    def getAllProfileNames(self) -> List[str]:
        """
        Get the names of all the profiles stored in the data storage.

        Returns:
            List[str]: A list of profile names or a message if empty.
        """
        if not self.profiles:
            return ["No profiles available, time to create some!"]
        else:
            return [profile.getName() for profile in self.profiles]

    def get_profile(self, profile_name: str) -> Optional[Profile]:
        """
        Get a profile from the data storage by its name.

        Args:
            profile_name (str): The name of the profile.

        Returns:
            Optional[Profile]: The profile object if found, None otherwise.
        """
        for profile in self.profiles:
            if profile.getName() == profile_name:
                return profile
        return None

    def get_attack(self,attack_id) -> Optional[Attack]:

        for attack in self.attacks:
            if attack.getID() == int(attack_id):
                return attack
        return None

    def prepare_data_to_remote_server(self) -> str:
        """
        Prepare the data before sending it to the remote server.

        Returns:
            str: A JSON string containing the profile data.
        """
        profiles = [profile.to_json() for profile in self.profiles]
        return json.dumps({'profiles': profiles})

    def save_data(self) -> None:
        """
        Save the data object to a file.
        """
        with open('data.pkl', 'wb') as file:
            pickle.dump(self, file)

    @classmethod
    def load_data(cls: Type['DataStorage']) -> 'DataStorage':
        """
        Load the data object from a file and return an instance.

        Returns:
            DataStorage: An instance of the DataStorage class.
        """
        if os.path.exists('data.pkl'):
            with open('data.pkl', 'rb') as file:
                loaded_data = pickle.load(file)
                cls._shared_state.update(loaded_data.__dict__)
        return cls()
