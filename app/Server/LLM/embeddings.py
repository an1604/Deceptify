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
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = faiss.IndexFlatL2(384)
        self.sentences_map = {}
        self.faq = self.get_faq(file_path='knowledgebase_custom.csv')

    @staticmethod
    def get_nearest_neighbors(vector, k=3):
        index = faiss.read_index(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'faiss.index'))
        query_vector = vector.astype("float32").reshape(1, -1)
        distances, indices = index.search(query_vector, k)
        return indices, distances

    def generate_faq_embedding(self):
        for qa in self.faq:  # Create the embedding representation for each row in the knowledgebase.
            embedding = self.get_embedding(qa)
            self.index.add(embedding)

        index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'faiss.index')
        faiss.write_index(self.index, index_path)

    def get_faq(self, file_path='knowledgebase_custom.csv'):
        df = pd.read_csv(file_path, sep=";").dropna()
        faq = []
        for x, y in df.values:
            faq.append(x)
            self.sentences_map[x] = y
        return faq

    def get_embedding(self, _input):
        embedding = self.embedding_model.encode(_input)
        return np.array([embedding])  # Ensure it returns a 2D array

    def get_answer_from_embedding(self, _input, threshold=0.9):
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
