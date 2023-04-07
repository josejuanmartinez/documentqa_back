import logging

from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

import pandas as pd

from constants.consts import PERSIST_DIR


class ChromaVectorStore:
    def __init__(self, collection):
        self.collection = collection
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma(self.collection, self.embeddings, persist_directory=PERSIST_DIR)

    def add_documents(self, documents):
        res = self.vector_store.add_documents(documents)
        self.persist()
        return res

    def persist(self):
        self.vector_store.persist()
        self.vector_store = None
        self.vector_store = Chroma(self.collection, self.embeddings, persist_directory=PERSIST_DIR)

    def similarity_search(self, query: str, items: int = None):
        if items is not None:
            return self.vector_store.similarity_search(query, k=items)
        else:
            return self.vector_store.similarity_search(query)
