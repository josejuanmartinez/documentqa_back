import logging
import os

from langchain.document_loaders import PyMuPDFLoader, TextLoader

from constants.consts import TMP_DIR

import pandas as pd

from vector_stores.faiss_store import FaissVectorStore


class FaissLoader:
    def __init__(self, collection):
        self.collection = collection
        self.store = FaissVectorStore(collection)
        if not os.path.isdir(TMP_DIR):
            os.mkdir(TMP_DIR)

    def show_collection_data(self):
        pass
        """logging.debug(f"NUMBER OF DOCUMENTS IN STORAGE: {self.store.vector_store._client.get_or_create_collection(self.collection).count()}")
        df = pd.read_parquet('indexes/chroma-collections.parquet')
        logging.debug(f"CHROMA COLLECTIONS:\n{df.to_json()}")
        df = pd.read_parquet('indexes/chroma-embeddings.parquet')
        logging.debug(f"CHROMA EMBEDDINGS:\n{df.to_json()}")"""

    def index_pdf(self, pdf_bytes):
        hash_file = f"{abs(hash(str(pdf_bytes)))}.tmp"
        filename = f"{TMP_DIR}{hash_file}"
        try:
            with open(filename, 'wb') as f:
                f.write(pdf_bytes)
            loader = PyMuPDFLoader(filename)
            docs = loader.load()
            self.store.add_documents(docs)
        except Exception as e:
            if os.path.exists(filename):
                os.remove(filename)
            raise e
        if os.path.exists(filename):
            os.remove(filename)

    def index_text(self, text):
        hash_file = f"{abs(hash(str(text)))}.tmp"
        filename = f"{TMP_DIR}{hash_file}"
        try:
            with open(filename, 'w') as f:
                f.write(text)
            loader = TextLoader(filename)
            docs = loader.load()
            self.store.add_documents(docs)
        except Exception as e:
            if os.path.exists(filename):
                os.remove(filename)
            raise e

        if os.path.exists(filename):
            os.remove(filename)

    def qa(self, query):
        self.store.similarity_search(query)
