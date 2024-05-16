"""
Acting like a session database,
Stores all the current information of the client, new attacks, profiles, recordings, etc.
After the session ends, this object will push all the information to the remote server to
save that in the database.
"""
import base64
import json
import os


class DataStorage:
    def __init__(self):
        self.profiles = set()
        self.prompts = set()

    def add_prompt(self, prompt): #check if a prompt already exist
        self.prompts.add(prompt)

    def get_prompts(self):
        return self.prompts

    def delete_prompt(self, prompt): #check if prompt exist
        self.prompts.remove(prompt)

    def prepare_data_to_remote_server(self):
        """Prepare the data before sending to the remote server."""

        profiles = [profile.to_json() for profile in self.profiles]
        prompts = [prompt.to_json() for prompt in self.prompts]
        return json.dumps({
            'profiles': profiles,
            'prompts': prompts
        })
