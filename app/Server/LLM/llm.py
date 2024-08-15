from langchain_community.llms import Ollama
from time import time
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
        self.init_msg = None

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
        self.init_msg = f"Hello {self.mimic_name}, its Jason from {attack_purpose}."

    def get_init_msg(self):
        return self.init_msg

    def generate_knowledgebase(self, gen_info):
        return self.llm.invoke(Prompts.KNOWLEDGEBASE_ROLE.format(gen_info=gen_info))

    def get_chat_history(self):
        return [msg for msg in self.chat_history.get_chat_history() if msg not in ['user', 'assistant']]

    def get_answer(self, prompt, event=None):
        self.chat_history.add_human_message(prompt)
        if not self.embedd_custom_knowledgebase:
            self.embedding_model.generate_faq_embedding()
            self.embedd_custom_knowledgebase = True

        answer, apply_active_learning = self.embedding_model.get_answer_from_embedding(prompt)
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

        if event:
            event.set()

        self.chat_history.add_ai_response(answer)

        if apply_active_learning:
            self.embedding_model.learn((prompt, answer))
        return answer


llm = Llm()
