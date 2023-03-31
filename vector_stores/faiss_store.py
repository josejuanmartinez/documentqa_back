import logging

from langchain import InMemoryDocstore
from langchain.docstore.base import Docstore
from langchain.schema import Document
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

from constants.consts import PERSIST_DIR


class FaissVectorStore:
    def __init__(self, collection):
        self.collection = collection
        self.embeddings = OpenAIEmbeddings()
        self.path = f"{PERSIST_DIR}/{self.collection}"
        try:
            self.vector_store = FAISS.load_local(self.path, self.embeddings)
        except:
            logging.warning(f"{self.path} not found. Creating...")
            self.vector_store = FAISS.from_texts([""], OpenAIEmbeddings())

    def add_documents(self, documents):
        res = self.vector_store.add_documents(documents)
        self.persist()
        return res

    def persist(self):
        self.vector_store.save_local(self.path)
        #self.vector_store = None
        #self.vector_store = Chroma(self.collection, self.embeddings, persist_directory=PERSIST_DIR)

    def similarity_search(self, query):
        return self.vector_store.similarity_search(query)
