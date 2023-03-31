import json

from constants import response_codes
from modules.indexing.loaders.text_loader import TextualLoader
from modules.indexing.querier import Querier
from app_secrets import Secrets
from io import BytesIO

import uvicorn
from fastapi import FastAPI, Request

import logging

from models.responses.generic import Generic
from modules.pdf.PDFExtractor import PDFExtractor

app = FastAPI()
secrets = Secrets.setup()


@app.get("/")
def root():
    return {"Hello": "World"}


@app.post("/process_pdf")
async def process_pdf(request: Request):
    form = await request.form()
    if 'file' not in form:
        return Generic(message="File 'file' not found in request", result="", code=response_codes.PARAM_NOT_FOUND)
    if 'query' not in form:
        return Generic(message="'query' not found in request", result="", code=response_codes.PARAM_NOT_FOUND)

    filename = form['file'].filename
    query = form['query']
    contents = await form['file'].read()
    logging.info(f"Processing {filename}")
    try:
        text = PDFExtractor.extract(BytesIO(contents))
        text_loader = TextualLoader(text)
        text_querier = Querier(text_loader)
        result = text_querier.query(query)

        return Generic(message=f"{filename} was successfully processed", result=json.dumps(result),
                       code=response_codes.SUCCESS)

    except Exception as e:
        return Generic(message=e, result="", code=10)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
