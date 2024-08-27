import os.path
from datetime import datetime
from langchain_community.llms import Ollama
from time import time
from app.Server.LLM.chat_history import chatHistory
from app.Server.LLM.embeddings import embeddings
from app.Server.LLM.prompts.prompts import Prompts
import re

# model_name = 'http://ollama:11434/'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY
model_name = 'llama3'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY

# machine = 'ollama'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY
machine = 'localhost'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY


class Llm(object):
    def __init__(self):
        self.llm = Ollama(model=model_name)  # Switched the Ollama to ChatOllama
        self.embedding_model = embeddings()
        self.chat_history = chatHistory()
        self.chat_history.initialize_role(Prompts.ROLE)
        self.user_prompt = self.chat_history.get_prompt()
        self.embedd_custom_knowledgebase = False
        self.mimic_name = 'Donald'  # Default value
        self.init_msg = None
        self.end_conv = False
        self.purpose = None

        self.finish_msg = None

    def flush(self):
        self.chat_history.flush()
        self.embedding_model.flush()

    def initialize_new_attack(self, attack_purpose, profile_name):
        self.end_conv = False
        self.finish_msg = None
        self.mimic_name = profile_name
        Prompts.set_role(attack_purpose=attack_purpose)  # Defining the new role according to the purpose.
        self.purpose = attack_purpose
        self.embedding_model.initialize_again(attack_purpose)  # Initialize the embedding with a purpose.

        self.chat_history.set_profile_name_for_transcript(profile_name)
        self.chat_history.initialize_role(Prompts.ROLE)
        self.user_prompt = self.chat_history.get_prompt()

        self.embedd_custom_knowledgebase = False
        # self.init_msg = f"Hello {self.mimic_name}, its Jason from {attack_purpose}."
        # self.chat_history.add_ai_response(self.init_msg)

    def validate_number(self, prompt):
        # Regular expression to find the number
        number = re.findall(r'\d+', prompt.replace(" ", "").replace("/", "").replace("\\", ""))
        # Convert the first match to an integer (or float if needed)
        if number:
            if self.purpose == "Bank":  # account number
                if int(number[0]) == 0:
                    return "This is not a real number"
                elif len(number[0]) == 6:
                    return "Thank you, we have solved the issue. Goodbye"

                else:
                    return "I need a 6 digit account number"
            elif self.purpose == "Hospital":
                if int(number[0]) == 0:
                    return "This is not a real number"
                elif len(number[0]) == 9:  # check for 0 at the start of the number
                    return "Thank you, we have opened your account. Goodbye"
                else:
                    return "I need a 9 digit ID"
        return None

    def get_init_msg(self):
        return self.init_msg

    def generate_knowledgebase(self, gen_info):
        return self.llm.invoke(Prompts.KNOWLEDGEBASE_ROLE.format(gen_info=gen_info))

    def get_chat_history(self):
        return [msg for msg in self.chat_history.get_chat_history() if msg not in ['user', 'assistant']]

    def get_answer_from_embedding(self,prompt):
        if not self.embedd_custom_knowledgebase:
            self.embedding_model.generate_faq_embedding()
            self.embedd_custom_knowledgebase = True
        self.chat_history.add_human_message(prompt)
        answer = self.embedding_model.get_answer_from_embedding(prompt)

        if answer:
            self.chat_history.add_ai_response(answer)

        return answer

    def get_answer(self, prompt):
        chain = self.user_prompt | self.llm

        answer = chain.invoke({
                "history": self.chat_history.get_chat_history(),
                'name': self.mimic_name,  # Default value
                # 'place': 'park',  # Default value
                # 'target': 'address',  # Default value
                # 'connection': 'co-worker',  # Default value,
                # 'principles': prompts.get_principles(),
                "time": datetime.now().time(),
                "context": prompt
            })
        self.chat_history.add_ai_response(answer)
        if 'bye' in answer.lower() or 'bye' in prompt.lower():
            self.end_conv = True
            self.finish_msg = answer
            # self.flush()

        return answer

    def get_finish_msg(self):
        if self.end_conv:
            return self.finish_msg

    def is_conversation_done(self):
        return self.end_conv


class llm_factory(object):
    @staticmethod
    def generate_new_attack(attack_type, profile_name):
        llm = Llm()
        llm.initialize_new_attack(attack_type, profile_name)
        return llm


llm = Llm()

# if __name__ == '__main__':
#    llm = Llm()
#    llm.initialize_new_attack("Bank", "Oded warem")
#    llm.get_answer("goodbye")
#    llm.get_answer(
#        "Based on your history can you tell me with a true or false answer if the person gave you the information")
