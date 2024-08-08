import os
import time
import faiss
import pandas as pd
from threading import Thread
from langchain_community.llms import Ollama
from scrapegraphai.graphs import SmartScraperGraph
from queue import Queue

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# model_name = 'http://ollama:11434/'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY
model_name = 'llama3'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY

# machine = 'ollama'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY
machine = 'localhost'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY

# Scraper configurations
graph_config = {
    "llm": {
        "model": "ollama/llama3",
        "temperature": 0,
        "format": "json",
        "base_url": f"http://{machine}:11434",
    },
    "embeddings": {
        "model": f"http://{machine}:11434/nomic-embed-text",
        "base_url": f"http://{machine}:11434",
    },
    "verbose": True,
}


class Llm(object):
    def __init__(self):
        self.llm = Ollama(model=model_name)
        self.scraper = None
        self.faq = None
        self.qa_q = Queue()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        self.start_conv = True
        self.stop = False
        self.embedd_custom_knowledgebase = False
        self.open_msg = 'Hello how are you doing?'

        # Create Faiss index
        self.index = faiss.IndexFlatL2(384)

    def generate_faq_embedding(self):
        for qa in self.faq:  # Create the embedding representation for each row in the knowledgebase.
            embedding = self.get_embedding(qa)
            self.index.add(embedding)

        index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'faiss.index')
        faiss.write_index(self.index, index_path)

    def generate_knowledgebase(self, gen_info):
        return self.llm.invoke(KNOWLEDGEBASE_ROLE.format(gen_info))

    def get_answer(self, prompt, history, event=None):
        # if self.start_conv:
        #     generate_embedding = Thread(target=self.add_new_line_for_embedding)
        #     generate_embedding.daemon = 1
        #     generate_embedding.start()
        #     self.start_conv = False

        if not self.embedd_custom_knowledgebase:
            self.faq = self.get_faq(file_path='C:\\colman\\Final project\\Deceptify\\app\\knowledgebase_custom.csv')
            self.generate_faq_embedding()

        prompt_embedding = self.get_embedding(prompt)  # Get the embedding representation for the prompt
        indices, distances = self.get_nearest_neighbors(prompt_embedding)
        closest_distance = distances[0][0]
        faq_index = indices[0][0]  # Taking the closest FAQ index

        threshold = 0.85

        if closest_distance < threshold:
            try:
                answer = self.faq[faq_index].split('-')[-1]
            except IndexError as e:
                print(f"IndexError: {e}")
                print(f"Index: {faq_index}, Length of faq: {len(self.faq)}")
                answer = "Sorry, I couldn't find an appropriate answer."
        else:
            user_prompt = ROLE.format(prompt=prompt,
                                      place='park', history=history, connection='Best Friend',
                                      target='address')
            answer = self.llm.invoke(user_prompt)

        if event:
            event.set()
        self.qa_q.put((prompt, answer))
        return answer

    def scrape(self, url, prompt):
        self.scraper = SmartScraperGraph(
            prompt=prompt,
            source=url,
            config=graph_config
        )
        result = self.scraper.run()
        print(result)
        return result

    def get_embedding(self, _input):
        embedding = self.embedding_model.encode(_input)
        return np.array([embedding])  # Ensure it returns a 2D array

    def end_conversation(self):
        self.qa_q.put(None)
        self.stop = True

    def add_new_line_for_embedding(self):
        print('run the new thread...')
        while not self.stop:
            data = self.qa_q.get()
            print(data)
            print("1")
            if data:
                print('data found!')
                question, answer = data[0], data[1]
                res = f"{question}-{answer}"
                res_emb = self.get_embedding(res)

                self.index.add(res_emb)
                index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'faiss.index')
                faiss.write_index(self.index, index_path)
                print('New embedding added!!')
        print("Ended embedding")

    @staticmethod
    def get_nearest_neighbors(vector, k=3):
        index = faiss.read_index(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'faiss.index'))
        query_vector = vector.astype("float32").reshape(1, -1)
        distances, indices = index.search(query_vector, k)
        return indices, distances

    @staticmethod
    def get_faq(file_path=r'C:\\colman\\Final project\\Deceptify\\app\\knowledgebase_custom.csv'):
        df = pd.read_csv(file_path, sep=";")
        faq = [x + " - " + y for x, y in df.values]
        return faq


llm = Llm()
