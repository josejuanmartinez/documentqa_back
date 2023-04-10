import logging
import random
from typing import List

from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter

from constants.consts import CHUNK_OVERLAP, CHUNK_SIZE, PARAGRAPH, AVG_SIZE_OF_PARAGRAPH, NEWLINE


class Splitter:
    def __init__(self, separator=None, chunk_size=None, chunk_overlap=None):
        if separator is None:
            separator = PARAGRAPH
        if chunk_size is None:
            chunk_size = CHUNK_SIZE
        if chunk_overlap is None:
            chunk_overlap = CHUNK_OVERLAP

        self.original_separator = separator
        self.separator = separator
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.splitter = CharacterTextSplitter(
            separator=self.separator,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

    def split(self, docs: List[Document]):
        docs = self.splitter.split_documents(docs)

        # I get random 5 splits and check the length. If the splits are too big, it means I need lower granularity.
        random_docs = random.sample(docs, k=min(len(docs), 5))
        for rd in random_docs:
            if len(rd.page_content) > AVG_SIZE_OF_PARAGRAPH:
                logging.warning("Splitter returned very big chunks. Replacing by newlines.")
                self.original_separator = self.separator
                self.separator = NEWLINE
                self.splitter = CharacterTextSplitter(
                    separator=self.separator,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    length_function=len,
                )

                docs = self.splitter.split_documents(docs)
                break

        return docs

