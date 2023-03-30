from io import BytesIO

import uvicorn
from fastapi import FastAPI, UploadFile

import logging

from modules.pdf.PDFExtractor import PDFExtractor

app = FastAPI()


@app.get("/")
def root():
    return {"Hello": "World"}


@app.post("/extract")
def extract(file: UploadFile):
    logging.info(f"Processing {file.filename}")
    try:
        contents = file.file.read()
        text = PDFExtractor.extract(BytesIO(contents))
    except Exception as e:
        return {"message": f"There was an error uploading the file: {e}"}
    finally:
        file.file.close()

    return {
        "message": f"Successfully uploaded {file.filename}",
        "result": text,
        "code": 0
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
