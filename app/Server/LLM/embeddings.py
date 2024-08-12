import os
from functools import lru_cache

import faiss
import numpy as np
import pandas as pd
from langchain_community.docstore import InMemoryDocstore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer


class embeddings(object):
    def __init__(self, knowledgebase=None):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = faiss.IndexFlatL2(384)

        self.knowledgebase = knowledgebase if knowledgebase is not None else 'clone'  # Clone for no-purpose attack

        self.json_filename_for_sentences_map = f'{self.knowledgebase}.json'
        self.sentences_map = {}

        # Fetch the correct csv file according the knowledgebase param.
        self.knowledgebase_file_path = None
        self.faq = None

    def get_nearest_neighbors(self, vector, k=3):
        index = faiss.read_index(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{self.knowledgebase}-faiss.index'))
        query_vector = vector.astype("float32").reshape(1, -1)
        distances, indices = index.search(query_vector, k)
        return indices, distances

    def flush(self):
        self.save_sentences_map()  # Saving the sentence map for feature extraction (reduce computation).
        self.sentences_map = {}

        self.knowledgebase_file_path = None
        self.json_filename_for_sentences_map = None
        self.faq = None
        self.knowledgebase = None
        self.index = faiss.IndexFlatL2(384)

    def initialize_again(self, knowledgebase):
        self.knowledgebase = knowledgebase
        self.json_filename_for_sentences_map = f'{self.knowledgebase}.json'
        self.init_knowledgebase_path(knowledgebase)
        self.faq = self.get_faq()

    def init_knowledgebase_path(self, knowledgebase):
        dire = os.path.dirname(os.path.abspath(__file__)) + '\\prompts\\'
        if knowledgebase is None:
            knowledgebase = 'knowledgebase_custom.csv'
            self.knowledgebase_file_path = os.path.join(dire, knowledgebase)
        else:
            self.knowledgebase_file_path = os.path.join(dire, f'{knowledgebase}-knowledge.csv')

    def save_sentences_map(self):
        sentences_map_json = json.dumps(self.sentences_map)
        with open(self.json_filename_for_sentences_map, 'w') as f:
            f.write(sentences_map_json)

    def generate_faq_embedding(self):
        for qa in self.faq:  # Create the embedding representation for each row in the knowledgebase.
            embedding = self.get_embedding(qa)
            self.index.add(embedding)

        index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{self.knowledgebase}-faiss.index')
        faiss.write_index(self.index, index_path)

    def get_faq(self):
        df = pd.read_csv(self.knowledgebase_file_path, sep=";").dropna()
        if not os.path.isfile(self.json_filename_for_sentences_map):
            faq = []
            for x, y in df.values:
                faq.append(x)
                self.sentences_map[x] = y
        else:
            faq = [x for x, _ in df.values]
            self.sentences_map = json.loads(self.json_filename_for_sentences_map)
        return faq

    def get_embedding(self, _input):
        embedding = self.embedding_model.encode(_input)
        return np.array([embedding])  # Ensure it returns a 2D array

    def get_answer_from_embedding(self, _input, threshold=0.7):
        print(_input)
        prompt_embedding = self.get_embedding(_input.lower())  # Get the embedding representation for the prompt
        indices, distances = self.get_nearest_neighbors(prompt_embedding)

        closest_distance = distances[0][0]
        print(closest_distance)
        faq_index = indices[0][0]  # Taking the closest FAQ index

        if closest_distance < threshold:
            try:
                answer = self.sentences_map[self.faq[faq_index]]
            except IndexError as e:
                print(f"IndexError: {e}")
                print(f"Cannot find the value for the given key: {self.faq[faq_index]}")
                answer = "Can you repeat it?"
        else:
            answer = None

        return answer
