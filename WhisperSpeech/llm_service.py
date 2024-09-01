import re
from datetime import datetime
from time import time

from langchain_community.llms.ollama import Ollama

from WhisperSpeech.prompts.prompts import Prompts

number_words = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
    "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
    "eighteen": "18", "nineteen": "19", "twenty": "20", "thirty": "30",
    "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70",
    "eighty": "80", "ninety": "90", "hundred": "100", "thousand": "1000"
}


class Llm(object):
    def __init__(self):
        self.llm = Ollama(model='llama3')  # Switched the Ollama to ChatOllama
        self.embedd_custom_knowledgebase = False
        self.init_msg = None
        self.end_conv = False
        self.purpose = None
        self.finish_msg = None

    def initialize_new_attack(self, attack_purpose, mimic_name):
        Prompts.set_role(attack_purpose=attack_purpose)  # Defining the new role according to the purpose.
        self.user_prompt = Prompts.ROLE
        self.mimic = mimic_name
        self.purpose = attack_purpose

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

    def get_answer(self, prompt, chat_history):
        time1 = time()
        chain = self.user_prompt | self.llm

        answer = chain.invoke({
            "history": chat_history,
            'name': self.mimic,  # Default value
            "time": datetime.now().time(),
            "context": prompt
        })
        if 'bye' in answer.lower() or 'bye' in prompt.lower():
            self.end_conv = True
            self.finish_msg = answer
        print(time() - time1)
        return answer


class llm_factory(object):
    @staticmethod
    def generate_new_attack(attack_type, mimic_name):
        llm = Llm()
        llm.initialize_new_attack(attack_type, mimic_name)
        return llm
