import os
import time
import faiss
import pandas as pd

from langchain_community.llms import Ollama
from scrapegraphai.graphs import SmartScraperGraph

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

ROLE = """
ROLE: Your name is Donald, you are the best friend of the other speaker, and you need to get his address to pick him up. .
REMEMBER: keep your answers as short as you can, max five words.
Query: {prompt}
Reference Answer: {reference}
"""

KNOWLEDGEBASE_ROLE = """
    Your task is to generate a knowledgebase like a csv that include general 
    questions and answers about a person.
    the answers should be short and simple
    The person have the following general information that you can use to generate the file:
    {}. 

    For example: If the person likes to play chess, for a question what's your plans today you can 
    insert an answer 'To play chess', another question could be: "where were you yesterday?", and an answer to that
    will be "I went to the park yesterday with my dog"
    """

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
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        self.start_conv = True
        self.open_msg = 'Hello how are you doing?'

        # Create Faiss index
        self.index = faiss.IndexFlatL2(384)
        self.faq = self.get_faq()
        self.generate_faq_embedding()

    def generate_faq_embedding(self):
        for qa in self.faq:  # Create the embedding representation for each row in the knowledgebase.
            embedding = self.get_embedding(qa)
            self.index.add(embedding)

        index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'faiss.index')
        faiss.write_index(self.index, index_path)

    def generate_knowledgebase(self, gen_info):
        return self.llm.invoke(KNOWLEDGEBASE_ROLE.format(gen_info))

    def get_answer(self, prompt, event=None):
        prompt_embedding = self.get_embedding(prompt)  # Get the embedding representation for the prompt
        indices, distances = self.get_nearest_neighbors(prompt_embedding)
        closest_distance = distances[0][0]
        faq_index = indices[0][0]  # Taking the closest FAQ index

        print(closest_distance)
        threshold = 0.85

        if closest_distance < threshold:
            try:
                answer = self.faq[faq_index].split('-')[-1]
            except IndexError as e:
                print(f"IndexError: {e}")
                print(f"Index: {faq_index}, Length of faq: {len(self.faq)}")
                answer = "Sorry, I couldn't find an appropriate answer."
        else:
            user_prompt = ROLE.format(prompt=prompt,reference=self.faq[faq_index].split('-')[-1])
            print(user_prompt)
            answer = self.llm.invoke(user_prompt)
        if event:
            event.set()
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

    @staticmethod
    def get_nearest_neighbors(vector, k=3):
        index = faiss.read_index(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'faiss.index'))
        query_vector = vector.astype("float32").reshape(1, -1)
        distances, indices = index.search(query_vector, k)
        return indices, distances

    @staticmethod
    def get_faq(file_path=r'C:\colman\Final project\Deceptify\app\Server\LLM\knowledge.csv'):
        df = pd.read_csv(file_path, sep=";")
        faq = [x + " - " + y for x, y in df.values]
        return faq


if __name__ == '__main__':
    llm = Llm()
    # llm.scrape()
    t1 = time.time()
    print(llm.get_answer("I will speak with you soon"))
    print(time.time() - t1)

