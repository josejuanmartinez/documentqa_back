import logging
from io import BytesIO
from typing import IO, Annotated, Union

from constants import response_codes
from constants.consts import COLLECTION
from modules.indexing.loaders.chroma_loader import ChromaLoader
from modules.indexing.querier import Querier
from app_secrets import Secrets

import uvicorn
from fastapi import FastAPI, Request, Form, File, UploadFile

from models.responses.generic import Generic
from modules.pdf.PDFExtractor import PDFExtractor

app = FastAPI()
secrets = Secrets.setup()
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

loader = ChromaLoader(COLLECTION)


@app.get("/")
def root():
    return {"Hello": "World"}


@app.post("/process_pdf")
async def process_pdf(file: Annotated[UploadFile, File()], separator: Union[str, None] = None,
                      chunk_size: Union[int, None] = None,  chunk_overlap: Union[int, None] = None):
    filename = file.filename
    extension = filename.split('.')[-1]
    if extension.lower() == 'pdf':
        contents = await file.read()
    else:
        return Generic(message="Only txt of pdf files supported at this point", result="",
                       code=response_codes.INVALID_FORMAT)
    logging.info(f"Processing {filename} with separator={separator}, chunk_size={chunk_size} and "
                 f"chunk_overlap={chunk_overlap}")
    try:
        loader.index_pdf(contents, filename, separator, chunk_size, chunk_overlap)
        return Generic(message=f"{filename} was successfully processed", result="",
                       code=response_codes.SUCCESS)

    except Exception as e:
        return Generic(message=str(e), result="", code=response_codes.EXCEPTION)


@app.post("/process_text")
async def process_text(file: Annotated[UploadFile, File()], separator: Union[str, None] = None,
                       chunk_size: Union[int, None] = None,  chunk_overlap: Union[int, None] = None):
    filename = file.filename
    extension = filename.split('.')[-1]
    if extension.lower() == 'txt':
        contents = await file.read()
    elif extension.lower() == 'pdf':
        content_bytes = await file.read()
        content_bytes_io = BytesIO(content_bytes)
        contents = PDFExtractor.extract(content_bytes_io)
    else:
        return Generic(message="Only txt of pdf files supported at this point", result="",
                       code=response_codes.INVALID_FORMAT)
    logging.info(f"Processing {filename} with separator={separator}, chunk_size={chunk_size} and "
                 f"chunk_overlap={chunk_overlap}")
    try:
        loader.index_text(contents, filename, separator, chunk_size, chunk_overlap)
        return Generic(message=f"{filename} was successfully processed", result="",
                       code=response_codes.SUCCESS)

    except Exception as e:
        return Generic(message=e, result="", code=response_codes.EXCEPTION)


@app.get("/query")
async def query(question):
    logging.info(f"Triggering {question} towards the index")

    try:
        querier = Querier(loader)
        result = querier.retrieve_first(question)

        return Generic(message=f"Processed: `{question}`", result=result,
                       code=response_codes.SUCCESS)

    except Exception as e:
        return Generic(message=e, result="", code=response_codes.EXCEPTION)


if __name__ == "__main__":
    loader.show_collection_data()
    uvicorn.run(app, host="0.0.0.0", port=5000)
