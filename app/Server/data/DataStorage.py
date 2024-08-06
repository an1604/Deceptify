import json
import os
import pickle
from typing import Set, List, Optional, Type

from app.Server.data.Profile import Profile
from app.Server.data.Attacks import Attack


class DataStorage:
    """
    A class that represents the data storage for profiles, prompts, and attacks.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DataStorage, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.profiles: Set[Profile] = set()
            self.attacks: Set = set()
            self._initialized = True

    def add_profile(self, profile: Profile) -> None:
        self.profiles.add(profile)

    def add_attack(self, new_attack: Attack) -> None:
        self.attacks.add(new_attack)
        # print(f'dataStorage attacks: {self.attacks}')

    def get_attacks(self) -> Set[Attack]:
        return self.attacks

    def delete_attack(self, attackID: int) -> None:
        attack_to_remove = None
        for attack in self.attacks:
            if attack.getID() == attackID:
                attack_to_remove = attack
                break
        if attack_to_remove:
            self.attacks.remove(attack_to_remove)

    def get_AllProfiles(self) -> Set[Profile]:
        return self.profiles

    def get_profiles(self) -> Set[Profile]:
        return self.profiles

    def getAllProfileNames(self) -> List[str]:
        if not self.profiles:
            return ["No profiles available, time to create some!"]
        else:
            return [profile.getName() for profile in self.profiles]

    def get_profile(self, profile_name: str) -> Optional[Profile]:
        for profile in self.profiles:
            if profile.getName() == profile_name:
                return profile
        return None

    def get_attack(self, attack_id: int) -> Optional[Attack]:
        for attack in self.attacks:
            if attack.getID() == attack_id:
                return attack
        return None

    def prepare_data_to_remote_server(self) -> str:
        profiles = [profile.to_json() for profile in self.profiles]
        return json.dumps({'profiles': profiles})

    def save_data(self) -> None:
        with open('data.pkl', 'wb') as file:
            pickle.dump(self, file)

    @classmethod
    def load_data(cls: Type['DataStorage']) -> 'DataStorage':
        instance = cls()
        if os.path.exists('data.pkl'):
            # print("The path exists!")
            with open('data.pkl', 'rb') as file:
                loaded_data = pickle.load(file)
                instance.__dict__.update(loaded_data.__dict__)
        return instance


class Data:
    _data_storage = None

    @staticmethod
    def get_data_object() -> DataStorage:
        if Data._data_storage is None:
            Data._data_storage = DataStorage.load_data()
        return Data._data_storage
