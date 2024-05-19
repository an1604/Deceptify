"""
Acting like a session database,
Stores all the current information of the client, new attacks, profiles, recordings, etc.
After the session ends, this object will push all the information to the remote server to
save that in the database.
"""
import base64
import json
import os
from Server.data.Profile import Profile
from typing import Set, List

class DataStorage:
    """
    A class that represents the data storage for profiles, prompts, and attacks.
    """

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
        if not self._shared_state:
            self.profiles = set()
            self.prompts = set()
            self.attacks = set()

    def add_prompt(self, prompt):
        """
        Add a prompt to the data storage.

        Args:
            prompt: The prompt to be added.
        """
        self.prompts.add(prompt)

    def get_prompts(self):
        """
        Get all the prompts stored in the data storage.

        Returns:
            A set of prompts.
        """
        return self.prompts

    def delete_prompt(self, desc):
        prompt = None
        for prt in self.prompts:
            if prt.prompt_desc == desc:
                prompt = prt
        self.prompts.remove(prompt)

    def add_profile(self, profile):
        """
        Add a profile to the data storage.

        Args:
            profile: The profile to be added.
        """
        self.profiles.add(profile)

    def add_attack(self, new_attack):
        """
        Add an attack to the data storage.
        This also adds the attack to the target and victim profiles.

        Args:
            new_attack: The attack to be added.
        """

        target = new_attack.get_target()
        victim = new_attack.get_mimic_profile()
        target.addAttack(new_attack)
        victim.addAttack(new_attack)
        self.attacks.add(new_attack)

    def get_attacks(self):
        """
        Get all the attacks stored in the data storage.

        Returns:
            A set of attacks.
        """
        return self.attacks

    def delete_attack(self, attackID):
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
        print(self.profiles)
        """
        Get all the profiles stored in the data storage.

        Returns:
            A set of profiles.
        """
        return self.profiles

    def get_profiles(self, attacker: bool = False) -> Set[Profile]:
        """
        Get the profiles stored in the data storage according to role.

        Args:
            attacker: A boolean indicating whether to get attacker profiles or victim profiles.

        Returns:
            A set of profiles.
        """
        if attacker:
            return [profile for profile in self.profiles if profile.role == "Attacker"]
        else:
            return [profile for profile in self.profiles if profile.role == "Victim"]

    def getAllProfileNames(self) -> List[str]:
        """
        Get the names of all the profiles stored in the data storage.

        Returns:
            A list of profile names or if empty a message.
        """
        if len(self.profiles) == 0:
            return ["No profiles available, time to create some!"]
        else:
            return [profile.getName() for profile in self.profiles]

    def get_profile(self, profile_name) -> Profile | None:
        """
        Get a profile from the data storage by its name.

        Args:
            profile_name: The name of the profile.

        Returns:
            The profile object if found, None otherwise.
        """
        for profile in self.profiles:
            if profile.getName() == profile_name:
                return profile
        return None

    def prepare_data_to_remote_server(self):
        """
        Prepare the data before sending it to the remote server.

        Returns:
            A JSON string containing the profiles and prompts data.
        """
        profiles = [profile.to_json() for profile in self.profiles]
        prompts = [prompt.to_json() for prompt in self.prompts]
        return json.dumps({
            'profiles': profiles,
            'prompts': prompts
        })
