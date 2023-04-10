import re


class WhitespaceNormalizer:
    def __init__(self):
        pass

    @staticmethod
    def normalize(text):
        norm_text = re.sub(r'[ \t]+\r', '\r', text)
        norm_text = re.sub(r'[ \t]+\n', '\n', norm_text)
        norm_text = re.sub(r'\r\n', '\n', norm_text)
        norm_text = re.sub(r'\r', '', norm_text)
        return norm_text
