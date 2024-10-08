import os.path
from datetime import datetime
from langchain_community.llms import Ollama
from time import time, sleep
from app.Server.LLM.chat_history import chatHistory
from app.Server.LLM.embeddings import embeddings
from app.Server.LLM.prompts.prompts import Prompts
import re
from app.requests_for_remote_server.llm_requests import *

# model_name = 'http://ollama:11434/'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY
model_name = 'llama3'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY

# machine = 'ollama'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY
machine = 'localhost'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY

number_words = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
    "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
    "eighteen": "18", "nineteen": "19", "twenty": "20", "thirty": "30",
    "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70",
    "eighty": "80", "ninety": "90", "hundred": "100", "thousand": "1000"
}


def replace_words_with_numbers(text):
    # Replace words with corresponding numbers
    for word, digit in number_words.items():
        text = text.replace(word, digit)
    return text


class Llm(object):
    def __init__(self):
        self.llm = Ollama(model=model_name)  # Switched the Ollama to ChatOllama
        self.embedding_model = embeddings()
        self.chat_history = chatHistory()
        self.chat_history.initialize_role(Prompts.ROLE)
        self.user_prompt = self.chat_history.get_prompt()
        self.embedd_custom_knowledgebase = False
        self.init_msg = None
        self.end_conv = False
        self.purpose = None
        self.finish_msg = None
        self.task_id = None
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
        # self.task_id = new_attack_request(profile_name, attack_purpose)
        # self.init_msg = f"Hello {self.mimic_name}, its Jason from {attack_purpose}."
        # self.chat_history.add_ai_response(self.init_msg)

    def validate_number(self, prompt):
        # Regular expression to find the number
        for word, dig in number_words.items():
            prompt = prompt.replace(word, dig)
        print(prompt)
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

    def get_answer_from_embedding(self, prompt):
        if not self.embedd_custom_knowledgebase:
            self.embedding_model.generate_faq_embedding()
            self.embedd_custom_knowledgebase = True
        self.chat_history.add_human_message(prompt)
        answer = self.embedding_model.get_answer_from_embedding(prompt)

        if answer:
            self.chat_history.add_ai_response(answer)

        return answer

    def get_answer(self, prompt):
        time1 = time()
        chain = self.user_prompt | self.llm
        answer = None
#        id = generate_answer_request(self.task_id, prompt, self.chat_history.get_chat_history())
#        if id is not None:
#            for i in range(10):
#                answer = get_llm_answer_request(id)
#                if answer:
#                    break
#                sleep(2.5)

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
        if answer:
            self.chat_history.add_ai_response(answer)
            if 'bye' in answer.lower() or 'bye' in prompt.lower():
                self.end_conv = True
                self.finish_msg = answer
                # self.flush()
        print(time() - time1)
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
#   llm = Llm()
#    llm.initialize_new_attack("Bank", "Oded warem")
#    llm.chat_history.add_ai_response("hello oded, this is jason from discount bank")
#    while True:
#        msg = input("type your message\n")
#        llm.chat_history.add_human_message(msg)
#        response = llm.get_answer_from_embedding(msg)
#        if response is None:
#            response = llm.validate_number(msg)
#            if response is None:
#                response = llm.get_answer(msg)
#        llm.chat_history.add_ai_response(response)
#        print(response)
