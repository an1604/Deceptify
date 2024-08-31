from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate, PromptTemplate
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class chatHistory(object):
    def __init__(self, name='default'):
        self.chat_history = []
        self.role = None
        self.name = name
        self.directory = "attack_records"
        logging.info(f"Initialized chatHistory with name: {self.name}")

    def set_profile_name_for_transcript(self, profile_name):
        self.name = profile_name
        logging.info(f"Profile name set for transcript: {profile_name}")

    def flush(self, save_attack=True):
        if save_attack:
            logging.info("Saving chat before flushing.")
            self.save_chat()
        self.chat_history.clear()
        self.role = None
        logging.info("Chat history flushed.")

    def save_chat(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
            logging.info(f"Created directory: {self.directory}")

        file_path = os.path.join(self.directory, "transcript.txt")
        with open(file_path, 'w') as f:
            for role, prompt in self.chat_history:
                f.write(f'{role}: {prompt}\n')
        logging.info("Chat history saved to file.")

    def initialize_role(self, role: SystemMessage):
        self.role = role
        logging.info(f"Role initialized: {role}")

    def add_human_message(self, msg: str):
        message = ("user", f"{msg}")
        self.chat_history.append(message)
        logging.info(f"Added human message: {msg}")

    def add_system_message(self, msg: str):
        self.chat_history.extend(SystemMessage(content=msg))
        logging.info(f"Added system message: {msg}")

    def add_ai_response(self, res: str):
        msg = ("assistant", f"{res}")
        self.chat_history.append(msg)
        logging.info(f"Added AI response: {res}")

    def get_window(self):
        return self.chat_history[-1]

    def get_chat_history(self):
        return self.chat_history

    def update_chat_history(self, user_message, ai_response):
        self.chat_history.extend([
            HumanMessage(content=user_message),
            AIMessage(content=ai_response)
        ])
        logging.info(f"Updated chat history with user message: {user_message} and AI response: {ai_response}")

    def get_prompt(self):
        return self.role

    def get_transcription(self):
        transcription = "\n".join(f"{role}: {msg}" for role, msg in self.chat_history) + "\n"
        logging.info("Generated transcription of chat history.")
        return transcription
