from typing import IO

from pypdf import PdfReader


class PDFExtractor:
    """
        Uses pypdf to retrieve text from native PDF
    """
    def __init__(self):
        pass

    @staticmethod
    def extract(file: IO):
        reader = PdfReader(file)
        text = []
        for i, page in enumerate(reader.pages):
            text.append(page.extract_text())
        return "".join(text)
