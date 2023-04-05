import logging
from io import BytesIO
from typing import Union, Annotated

from constants import response_codes
from constants.consts import COLLECTION, HOST, PORT
from modules.indexing.loaders.chroma_loader import ChromaLoader
from modules.indexing.querier import Querier
from app_secrets import Secrets

import uvicorn
from fastapi import FastAPI, UploadFile, Query, Form

from models.responses.generic_schema import GenericSchema
from modules.pdf.PDFExtractor import PDFExtractor
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)

secrets = Secrets.setup()
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

loader = ChromaLoader(COLLECTION)


@app.get("/healthcheck", status_code=200)
async def healthcheck():
    """
    This endpoint is meant to provide a reliable method to check if the back end is up and running.
    """
    return GenericSchema(message="Healthy", result="", code=response_codes.SUCCESS)


@app.post("/process_pdf")
async def process_pdf(file: Annotated[UploadFile, Form(description="Your txt or pdf file to calculate embeddings and "
                                                                   "index them.")],
                      separator: Annotated[Union[str, None], Form(description="The separator to split your document in "
                                                                              "smaller chunks to be indexed. By "
                                                                              "default, '\n' since PDF extractors often"
                                                                              " remove multiple '\n'")],
                      chunk_size: Annotated[Union[int, None], Form(description="After splitting `file` into chunks by "
                                                                               "using `separator`, we create small "
                                                                               "chunks of `chunk_size`. By default, "
                                                                               "500.")],
                      chunk_overlap: Annotated[Union[int, None], Form(description="In order to take context into "
                                                                                  "consideration, chunks also get a "
                                                                                  "surrounding context of a total of "
                                                                                  "`chunk_overlap` previous and "
                                                                                  "following characters")]
                      ):
    """
    This endpoint receives a pdf file and indexes its embeddings in the configured vector store (by default, ChromaDB)
    using LangChain default PDF processor.

    Args:\n\n
    - `file`: Your PDF file to calculate embeddings and index them.
    - `separator`:  The separator to split your document in smaller chunks to be indexed. By default, '\\n' since PDF
    extractors often remove multiple '\\n'.\n
    - `chunk_size`: After splitting **file into chunks by using `separator`, we create small chunks of **chunk_size**.
    By default, 500.\n
    - `chunk_overlap`: In order to take context into consideration, chunks also get a surrounding context of a total of
    **chunk_overlap** previous and following characters.\n

    Returns:\n\n
         a json response with fields: message, code, result
    """
    if file is None:
        return GenericSchema(message="File is None", result="", code=response_codes.EXCEPTION)
    filename = file.filename
    extension = filename.split('.')[-1]
    if extension.lower() == 'pdf':
        contents = await file.read()
    else:
        return GenericSchema(message="Only txt of pdf files supported at this point", result="",
                             code=response_codes.INVALID_FORMAT)
    logging.info(f"Processing {filename} with separator={separator}, chunk_size={chunk_size} and "
                 f"chunk_overlap={chunk_overlap}")
    try:
        loader.index_pdf(contents, filename, separator, chunk_size, chunk_overlap)
        return GenericSchema(message=f"{filename} was successfully processed", result="",
                             code=response_codes.SUCCESS)

    except Exception as e:
        return GenericSchema(message=str(e), result="", code=response_codes.EXCEPTION)


@app.post("/process_text")
async def process_text(file: Annotated[UploadFile, Form(description="Your txt or pdf file to calculate embeddings and "
                                                                    "index them.")],
                       separator: Annotated[Union[str, None], Form(description="The separator to split your document in"
                                                                               " smaller chunks to be indexed. By "
                                                                               "default, '\n' since PDF extractors "
                                                                               "often remove multiple '\n'")],
                       chunk_size: Annotated[Union[int, None], Form(description="After splitting `file` into chunks by "
                                                                                "using `separator`, we create small "
                                                                                "chunks of `chunk_size`. By default, "
                                                                                "500.")],
                       chunk_overlap: Annotated[Union[int, None], Form(description="In order to take context into "
                                                                                   "consideration, chunks also get a "
                                                                                   "surrounding context of a total of "
                                                                                   "`chunk_overlap` previous and "
                                                                                   "following characters")]
                       ):
    """
     This endpoint receives a txt file and indexes its embeddings in the configured vector store (by default, ChromaDB).
     It can also receive a pdf file but it will convert it to text first using PyPDF.

     Args:\n\n
     - `file`: Your txt or pdf file to calculate embeddings and index them.
     - `separator`:  The separator to split your document in smaller chunks to be indexed. By default, '\\n' since PDF
     extractors often remove multiple '\\n'.\n
     - `chunk_size`: After splitting **file into chunks by using `separator`, we create small chunks of **chunk_size**.
     By default, 500.\n
     - `chunk_overlap`: In order to take context into consideration, chunks also get a surrounding context of a total of
     **chunk_overlap** previous and following characters.\n

     Returns:\n\n
          a json response with fields: message, code, result
     """
    filename = file.filename
    extension = filename.split('.')[-1]
    if extension.lower() == 'txt':
        contents = await file.read()
    elif extension.lower() == 'pdf':
        content_bytes = await file.read()
        content_bytes_io = BytesIO(content_bytes)
        contents = PDFExtractor.extract(content_bytes_io)
    else:
        return GenericSchema(message="Only txt of pdf files supported at this point", result="",
                             code=response_codes.INVALID_FORMAT)
    logging.info(f"Processing {filename} with separator={separator}, chunk_size={chunk_size} and "
                 f"chunk_overlap={chunk_overlap}")
    try:
        loader.index_text(contents, filename, separator, chunk_size, chunk_overlap)
        return GenericSchema(message=f"{filename} was successfully processed", result="",
                             code=response_codes.SUCCESS)

    except Exception as e:
        return GenericSchema(message=e, result="", code=response_codes.EXCEPTION)


@app.get("/query", tags=['query'])
async def query(question: str = Query(None, description="The search you want to do in Natural Language.")):
    """
        This endpoint will trigger your Vector Store database looking for the min cosine distance towards all the chunks
        previously indexed.

    Args:\n\n
    - `question`: The search you want to do in Natural Language.

    Returns:\n\n
        a json response with fields: `message`, `code` and `result`
    """
    logging.info(f"Triggering {question} towards the index")

    try:
        querier = Querier(loader)
        result = querier.retrieve_first(question)

        return GenericSchema(message=f"Processed: `{question}`", result=result,
                             code=response_codes.SUCCESS)

    except Exception as e:
        return GenericSchema(message=e, result="", code=response_codes.EXCEPTION)


if __name__ == "__main__":
    loader.show_collection_data()
    uvicorn.run(app, host=HOST, port=PORT)
