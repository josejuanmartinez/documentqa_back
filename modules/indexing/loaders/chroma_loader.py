import logging
import os
from langchain.document_loaders import PyMuPDFLoader, TextLoader

from constants.consts import TMP_DIR
from modules.splitters.paragraph_splitter import ParagraphSplitter
from modules.splitters.sentence_splitter import SentenceSplitter
from vector_stores.chroma_store import ChromaVectorStore

import pandas as pd


class ChromaLoader:
    def __init__(self, collection):
        self.collection = collection
        self.store = ChromaVectorStore(collection)
        if not os.path.isdir(TMP_DIR):
            os.mkdir(TMP_DIR)

    def show_collection_data(self):
        docs = self.store.vector_store._client.get_or_create_collection(self.collection).count()
        logging.debug(f"NUMBER OF DOCUMENTS IN STORAGE: {docs}")
        if docs > 0:
            df = pd.read_parquet('indexes/chroma-collections.parquet')
            logging.debug(f"CHROMA COLLECTIONS:\n{df.to_json()}")
            df = pd.read_parquet('indexes/chroma-embeddings.parquet')
            logging.debug(f"CHROMA EMBEDDINGS:\n{df.to_json()}")

    def index_pdf(self, pdf_bytes):
        hash_file = f"{abs(hash(str(pdf_bytes)))}.tmp"
        filename = f"{TMP_DIR}{hash_file}"
        try:
            with open(filename, 'wb') as f:
                f.write(pdf_bytes)
            loader = PyMuPDFLoader(filename)
            docs = loader.load()
            for d in docs:
                d.metadata['uploaded_filename'] = filename
            docs = SentenceSplitter().split(docs)
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
            for d in docs:
                d.metadata['uploaded_filename'] = filename
            docs = SentenceSplitter().split(docs)
            self.store.add_documents(docs)
        except Exception as e:
            if os.path.exists(filename):
                os.remove(filename)
            raise e

        if os.path.exists(filename):
            os.remove(filename)

    def qa(self, query):
        return self.store.similarity_search(query)
