import json
import os
import pickle
from typing import Set, List, Optional, Type

from app.Server.data.Profile import Profile
from app.Server.data.AiAttack import AiAttack


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
            self.ai_attacks: Set = set()
            self._initialized = True

    def add_profile(self, profile: Profile) -> None:
        self.profiles.add(profile)

    def add_ai_attack(self, new_ai_attack: AiAttack) -> None:
        self.ai_attacks.add(new_ai_attack)

    def get_ai_attacks(self) -> Set[AiAttack]:
        return self.ai_attacks

    def get_ai_attack(self, attack_id):
        attack = [attack for attack in self.ai_attacks if attack.getID() == int(attack_id)][0]
        return attack

    def delete_ai_attack(self, attackID: int) -> None:
        attack_to_remove = None
        for attack in self.ai_attacks:
            if attack.getID() == attackID:
                attack_to_remove = attack
                break
        if attack_to_remove:
            self.ai_attacks.remove(attack_to_remove)

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
