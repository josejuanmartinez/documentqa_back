from fastapi import UploadFile
from pydantic import BaseModel


class QAModel(BaseModel):
    file: UploadFile
    query: str
