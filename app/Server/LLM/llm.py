# from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from queue import Queue

from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser

from app.Server.LLM.chat_history import chatHistory
from app.Server.LLM.embeddings import embeddings
from app.Server.LLM.prompts.prompts import prompts

# model_name = 'http://ollama:11434/'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY
model_name = 'llama3'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY
# model_name = 'tinyllama'

# machine = 'ollama'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY
machine = 'localhost'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY


class Llm(object):
    def __init__(self):
        self.llm = ChatOllama(model=model_name)  # Switched the Ollama to ChatOllama
        self.parser = StrOutputParser()
        self.faq = None
        self.qa_q = Queue()

        self.embedding_model = None

        self.chat_history = chatHistory()
        self.chat_history.initialize_role(prompts.ROLE)

        self.start_conv = True
        self.stop = False
        self.embedd_custom_knowledgebase = False
        self.open_msg = 'Hello how are you doing?'

    def generate_knowledgebase(self, gen_info):
        return self.llm.invoke(prompts.KNOWLEDGEBASE_ROLE.format(gen_info=gen_info))

    def get_answer(self, prompt, history, event=None):
        try:
            # Creating HumanMessage object for ollama to understand.
            self.chat_history.add_human_message(prompt)

            if not self.embedd_custom_knowledgebase:
                self.embedding_model = embeddings()
                self.embedd_custom_knowledgebase = True

            answer = self.embedding_model.get_answer_from_embedding(prompt)
            if answer is None:
                # user_prompt = prompts.get_role(role=ROLE, history=history, prompt=prompt)
                chain = prompt | self.llm
                answer = chain.invoke({
                    "chat_history": self.chat_history.get_chat_history()
                }).content

            if event:
                event.set()

            self.qa_q.put((prompt, answer))
            self.chat_history.add_ai_response(AIMessage(content=answer))

            return answer

        except Exception as e:
            print(f"Exception from get_answer: {e}")

    def end_conversation(self):
        self.qa_q.put(None)
        self.stop = True


llm = Llm()
