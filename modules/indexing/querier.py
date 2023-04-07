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

    def retrieve(self, query, context=None, items=None):
        return self.loader.qa(query, context, items)

    """
    def retrieve_first(self, query, only_text=False):
        response_dict = {'text': self.loader.qa(query)[0].page_content, 'metadata': {}}
        if not only_text:
            response_dict['metadata'] = self.loader.qa(query)[0].metadata
        return response_dict
    """