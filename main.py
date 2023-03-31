import json
import logging

from constants import response_codes
from constants.consts import COLLECTION
from modules.indexing.loaders.chroma_loader import ChromaLoader
from modules.indexing.querier import Querier
from app_secrets import Secrets

import uvicorn
from fastapi import FastAPI, Request

from models.responses.generic import Generic

app = FastAPI()
secrets = Secrets.setup()
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

loader = ChromaLoader(COLLECTION)


@app.get("/")
def root():
    return {"Hello": "World"}


@app.post("/process_pdf")
async def process_pdf(request: Request):
    form = await request.form()
    if 'file' not in form:
        return Generic(message="File 'file' not found in request", result="", code=response_codes.PARAM_NOT_FOUND)
    filename = form['file'].filename
    contents = await form['file'].read()
    logging.info(f"Processing {filename}")
    try:
        loader.index_pdf(contents)
        return Generic(message=f"{filename} was successfully processed", result="",
                       code=response_codes.SUCCESS)

    except Exception as e:
        return Generic(message=e, result="", code=response_codes.EXCEPTION)


@app.post("/process_text")
async def process_text(request: Request):
    form = await request.form()
    if 'file' not in form:
        return Generic(message="File 'file' not found in request", result="", code=response_codes.PARAM_NOT_FOUND)

    filename = form['file'].filename
    contents = await form['file'].read()
    logging.info(f"Processing {filename}")
    try:
        loader.index_text(contents)
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
