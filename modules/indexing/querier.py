from langchain.chains.question_answering import load_qa_chain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.llms import OpenAI

# from modules.indexing.loaders.faiss_loader import FaissLoader
from modules.indexing.loaders.chroma_loader import ChromaLoader


class Querier:
    def __init__(self, loader: ChromaLoader):
        self.loader = loader
        self.chain = load_qa_chain(llm=OpenAI())
        self.sources_chain = load_qa_with_sources_chain(llm=OpenAI())

    def retrieve(self, query: str, items: int = None) -> []:
        """
        Retrieves `items` number of answers from the vector store answering to the query.
        Args:
            query: the question
            items: the number of items

        Returns:
            A list of rows from the vector store answering to that query
        """
        return self.loader.qa(query, items)