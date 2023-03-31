from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator

from constants.consts import TMP_DIR


class TextualLoader:
    def __init__(self, text):
        """
            LangChain expects only a file at current versions, so I will create a tmp file with the text.
        :param text:
        """
        hash_file = f"{hash(text)}.tmp"
        filename = f"{TMP_DIR}{hash_file}"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
        loader = TextLoader(filename)
        self.index = VectorstoreIndexCreator().from_loaders([loader])

