from langchain.document_loaders import PyMuPDFLoader
from langchain.indexes import VectorstoreIndexCreator

from constants.consts import TMP_DIR


class PDFLoader:
    def __init__(self, pdf_bytes):
        """
            LangChain expects only a file at current versions, so I will create a tmp file with the text.
        :param pdf_bytes: PDF bytes
        """
        hash_file = f"{hash(str(pdf_bytes))}.tmp"
        filename = f"{TMP_DIR}{hash_file}"
        with open(filename, 'wb') as f:
            f.write(pdf_bytes)
        loader = PyMuPDFLoader(filename)
        self.index = VectorstoreIndexCreator().from_loaders([loader])
        # faiss_index = FAISS.from_documents(self.index., OpenAIEmbeddings())

