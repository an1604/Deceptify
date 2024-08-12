from langchain_community.llms import Ollama
from queue import Queue
from time import time
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from app.Server.LLM.chat_history import chatHistory
from app.Server.LLM.embeddings import embeddings
from app.Server.LLM.prompts.prompts import Prompts

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

    def flush(self):
        self.chat_history.flush()
        self.embedding_model.flush()

    def initialize_new_attack(self, attack_purpose, profile_name):
        self.mimic_name = profile_name
        Prompts.set_role(attack_purpose=attack_purpose)  # Defining the new role according to the purpose.

        self.embedding_model.initialize_again(attack_purpose)  # Initialize the embedding with a purpose.

        self.chat_history.set_profile_name_for_transcript(profile_name)
        self.chat_history.initialize_role(Prompts.ROLE)
        self.user_prompt = self.chat_history.get_prompt()

        self.embedd_custom_knowledgebase = False

    def generate_knowledgebase(self, gen_info):
        return self.llm.invoke(Prompts.KNOWLEDGEBASE_ROLE.format(gen_info=gen_info))

    def get_answer(self, prompt, history=None, event=None):
        # try:
            # Creating HumanMessage object for ollama to understand.
            self.chat_history.add_human_message(prompt)
            if not self.embedd_custom_knowledgebase:
                self.embedding_model.generate_faq_embedding()
                self.embedd_custom_knowledgebase = True

            answer = self.embedding_model.get_answer_from_embedding(prompt)
            if answer is None:
                # user_prompt = prompts.get_role(role=ROLE, history=history, prompt=prompt)
                chain = self.user_prompt | self.llm
                time1 = time()
                answer = chain.invoke({
                    "history": self.chat_history.get_chat_history(),
                    'name': self.mimic_name,  # Default value
                    # 'place': 'park',  # Default value
                    # 'target': 'address',  # Default value
                    # 'connection': 'co-worker',  # Default value,
                    # 'principles': prompts.get_principles(),
                    "context": prompt
                })
                print(time() - time1)
            print("line 62")

            if event:
                event.set()

            self.chat_history.add_ai_response(answer)
            print("line 69")

            return answer
        # except Exception as e:
        #     print(f"Exception from get_answer: {e}")


llm = Llm()

if __name__ == '__main__':
    llm = Llm()
    llm.initialize_new_attack("Bank", "david")
    initial_message = "Hello this is Jason from Discount bank"
    llm.chat_history.add_ai_response(initial_message)
    print(initial_message)
    while True:
        user_response = input('user turn:')
        response = llm.get_answer(user_response)
        print(response)
