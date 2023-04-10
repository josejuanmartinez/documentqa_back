from typing import IO
import re
from pypdf import PdfReader


class PDFExtractor:
    """
        Uses pypdf to retrieve text from native PDF
    """
    def __init__(self):
        pass

    @staticmethod
    def normalize_spaces(text:str) -> str:
        text = text.replace('\r\n', '\n')
        text = re.sub(r'[ \t]+\n', '\n', text)
        return text

    @staticmethod
    def extract(file: IO) -> str:
        reader = PdfReader(file)
        text = []
        for i, page in enumerate(reader.pages):
            page_text = PDFExtractor.normalize_spaces(page.extract_text())
            text.append(page_text)
        return "".join(text)
