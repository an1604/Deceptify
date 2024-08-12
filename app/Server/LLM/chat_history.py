from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate, PromptTemplate


class chatHistory(object):
    def __init__(self, name='default'):
        self.chat_history = []
        self.role = None
        self.name = name

    def set_profile_name_for_transcript(self, profile_name):
        self.name = profile_name

    def flush(self, save_attack=True):
        if save_attack:
            self.save_chat()
        self.chat_history.clear()
        self.role = None

    def save_chat(self):
        with open(f'chat_history-{self.name}.txt', 'w') as f:
            for e in self.chat_history:
                f.write(e + '\n')

    def initialize_role(self, role: SystemMessage):
        self.role = role

    def add_human_message(self, msg: str):
        # self.chat_history.extend(HumanMessage(msg))
        self.chat_history.extend(("user", f"{msg}"))

    def add_system_message(self, msg: str):
        self.chat_history.extend(SystemMessage(content=msg))

    def add_ai_response(self, res: str):
        # self.chat_history.extend(AIMessage(content=res))
        self.chat_history.extend(("assistant", f"{res}"))

    def get_window(self):
        return self.chat_history[-1]

    def get_chat_history(self):
        return self.chat_history

    def update_chat_history(self, user_message, ai_response):
        self.chat_history.extend([
            HumanMessage(content=user_message),
            AIMessage(content=ai_response)
        ])

    def get_prompt(self):
        return self.role
