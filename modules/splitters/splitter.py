from typing import List

from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter

from constants.consts import CHUNK_OVERLAP, CHUNK_SIZE, PARAGRAPH


class Splitter:
    def __init__(self, separator=None, chunk_size=None, chunk_overlap=None):
        if separator is None:
            separator = PARAGRAPH
        if chunk_size is None:
            chunk_size = CHUNK_SIZE
        if chunk_overlap is None:
            chunk_overlap = CHUNK_OVERLAP
        self.splitter = CharacterTextSplitter(
            separator=separator,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def split(self, docs: List[Document]):
        return self.splitter.split_documents(docs)
