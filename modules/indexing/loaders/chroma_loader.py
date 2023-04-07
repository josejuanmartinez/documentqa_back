import logging
import os
from langchain.document_loaders import PyMuPDFLoader, TextLoader

from constants.consts import TMP_DIR

from modules.splitters.splitter import Splitter
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

    def index_pdf(self, pdf_bytes: bytes, filename: str, separator: str = None, chunk_size: int = None,
                  chunk_overlap: int = None):
        # hash_file = f"{abs(hash(str(pdf_bytes)))}.tmp"
        dir_filename = f"{TMP_DIR}{filename}"
        try:
            with open(dir_filename, 'wb') as f:
                f.write(pdf_bytes)
            loader = PyMuPDFLoader(dir_filename)
            docs = loader.load()
            for d in docs:
                d.metadata['uploaded_filename'] = filename
            docs = Splitter(separator, chunk_size, chunk_overlap).split(docs)
            self.store.add_documents(docs)
        except Exception as e:
            if os.path.exists(dir_filename):
                os.remove(dir_filename)
            raise e
        if os.path.exists(dir_filename):
            os.remove(dir_filename)

    def index_text(self, text: str, filename: str, separator: str = None, chunk_size: int = None,
                   chunk_overlap: int = None):
        # hash_file = f"{abs(hash(text))}.tmp"
        dir_filename = f"{TMP_DIR}{filename}"
        try:
            with open(dir_filename, 'w', encoding='utf-8') as f:
                f.write(text)
            loader = TextLoader(dir_filename, encoding='utf-8')
            docs = loader.load()
            for d in docs:
                d.metadata['uploaded_filename'] = filename
            docs = Splitter(separator, chunk_size, chunk_overlap).split(docs)
            self.store.add_documents(docs)
        except Exception as e:
            if os.path.exists(dir_filename):
                os.remove(dir_filename)
            raise e

        if os.path.exists(dir_filename):
            os.remove(dir_filename)

    def qa(self, query: str, context: str = None, items: int = None):
        if context is not None:
            query = f"{context}.\n\n. {query}"

        return self.store.similarity_search(query, items)
