from typing import List

from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter

from constants.consts import CHUNK_OVERLAP, CHUNK_SIZE


class ParagraphSplitter:
    def __init__(self):
        self.splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )

    def split(self, docs: List[Document]):
        return self.splitter.split_documents(docs)
