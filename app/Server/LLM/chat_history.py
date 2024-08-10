from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate


class chatHistory(object):
    def __init__(self):
        self.chat_history = []
        self.role = None

    def initialize_role(self, role: SystemMessage):
        self.role = role

    def generate_prompt(self, _input):
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.role),
            MessagesPlaceholder("chat_history"),
            ("human", f"{_input}"),
        ])
        return prompt

    def add_human_message(self, msg: str):
        self.chat_history.extend(HumanMessage(content=msg))

    def add_system_message(self, msg: str):
        self.chat_history.extend(SystemMessage(content=msg))

    def add_ai_response(self, res: str):
        self.chat_history.extend(AIMessage(content=res))

    def get_window(self):
        return self.chat_history[-1]

    def get_chat_history(self):
        return self.chat_history

    def update_chat_history(self, user_message, ai_response):
        self.chat_history.extend([
            HumanMessage(content=user_message),
            AIMessage(content=ai_response)
        ])
