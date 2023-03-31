from typing import Union

from langchain.chains.question_answering import load_qa_chain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.llms import OpenAI

from modules.indexing.loaders.pdf_loader import PDFLoader
from modules.indexing.loaders.text_loader import TextualLoader


class Querier:
    def __init__(self, loader: Union[PDFLoader, TextualLoader]):
        self.loader = loader
        self.chain = load_qa_chain(llm=OpenAI())
        self.sources_chain = load_qa_with_sources_chain(llm=OpenAI())

    def query(self, query):
        return self.loader.index.query_with_sources(query, llm=OpenAI())
