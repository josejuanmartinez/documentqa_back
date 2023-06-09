import logging
import datetime
import os
from io import BytesIO
from typing import  Annotated, Optional

import keyring
import nltk

from constants import response_codes
from constants.consts import COLLECTION, HOST, PORT, RELEVANT_THRESHOLD, \
    NOT_ENOUGH_RESULTS_TO_GENERATE_ANSWER, AUTHENTICATED, NEWLINE, CHUNK_SIZE, CHUNK_OVERLAP
from constants.response_codes import LOGIN_FAILED
from modules.generators.answer_generator import AnswerGenerator
from modules.indexing.loaders.chroma_loader import ChromaLoader
from modules.indexing.querier import Querier
from app_secrets import Secrets

import uvicorn
from fastapi import FastAPI, UploadFile, Form

from models.responses.generic_schema import GenericSchema
from modules.pdf.PDFExtractor import PDFExtractor
from fastapi.middleware.cors import CORSMiddleware

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

import jwt

from users.add_key import SERVICE_ID

# SECRETS
# =======
print("Checking secrets...")
if not Secrets.check():
    exit(1)
# =======

# LOGGING
# =======
print("Configuring logger...")
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)
# =======


# CHROMA
# =======
print("Setting up the vector store...")
loader = ChromaLoader(COLLECTION)
# =======

# NLTK
# =======
print("Installing small NLTK tools...")
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
# =======

# FAST API
# ========
print("Preparing FastAPI...")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)


# =========


@app.get("/healthcheck", status_code=200)
async def healthcheck():
    """
    This endpoint is meant to provide a reliable method to check if the back end is up and running.
    """
    return GenericSchema(message="Healthy", result="", code=response_codes.SUCCESS)


@app.post("/login", status_code=200)
async def login(email: Annotated[str, Form(description="User's email")],
                password: Annotated[str, Form(description="User's password")]):
    """
        This endpoint provides with login functionality based on email and password to be stored in keyring.

    Args:\n\n
        `email`: User's email
        `password`: User's password

    Returns:\n\n
         a json response with fields: `message`, `code`, `result`
    """

    # Define the payload for the token
    payload = {'email': email, 'password': password}

    if password != keyring.get_password(SERVICE_ID, email):
        return GenericSchema(message=f"Login failed", result="",
                             code=LOGIN_FAILED)

    # Generate the JWT token
    token = jwt.encode(payload, os.environ['KEYRING_SECRET_KEY'], algorithm='HS256')
    expires_in = datetime.datetime.utcnow() + datetime.timedelta(days=30)

    timestamp = expires_in.timestamp()
    return GenericSchema(message=f"Login successful", result={"token": token,
                                                              "expiresIn": timestamp,
                                                              "authUserState": AUTHENTICATED},
                         code=response_codes.SUCCESS)


@app.post("/lemmatize_stopwords")
async def lemmatize_stopwords(text: Annotated[str, Form(description="String to return with stopwords removed")],
                              lan: Annotated[str, Form(description="Language of the text")]):
    """
    This endpoint receives a string text and returns it lemmatized without any stopword.

    Args:\n\n
    - `text`: String to return with stopwords removed.
    - `lan`: Language of the text.

    Returns:\n\n
         a json response with fields: `message`, `code`, `result` where  in result you have the string without stop
         words.
    """
    try:
        lemmatizer = WordNetLemmatizer()
        text_tokens = word_tokenize(text, language=lan)

        result = " ".join([lemmatizer.lemmatize(word.lower()) for word in text_tokens
                           if lemmatizer.lemmatize(word.lower()) not in stopwords.words(lan)])
        return GenericSchema(message=f"Lemmas and Stopwords were successfully calculated", result=result,
                             code=response_codes.SUCCESS)
    except Exception as e:
        return GenericSchema(message=str(e), result="", code=response_codes.EXCEPTION)


@app.post("/lemmatize")
async def lemmatize(text: Annotated[str, Form(description="String to return with stopwords removed")],
                    lan: Annotated[str, Form(description="Language of the text")]):
    """
    This endpoint receives a string text and returns it lemmatized.

    Args:\n\n
    - `text`: String to return lemmatized.
    - `lan`: Language of the text.

    Returns:\n\n
         a json response with fields: `message`, `code`, `result` where  in result you have the string lemmatized.
    """
    try:
        lemmatizer = WordNetLemmatizer()
        text_tokens = word_tokenize(text, language=lan)

        result = " ".join([lemmatizer.lemmatize(word.lower()) for word in text_tokens])
        return GenericSchema(message=f"Lemmas were successfully calculated", result=result,
                             code=response_codes.SUCCESS)
    except Exception as e:
        return GenericSchema(message=str(e), result="", code=response_codes.EXCEPTION)


@app.post("/process_pdf")
async def process_pdf(file: Annotated[UploadFile, Form(description="Your txt or pdf file to calculate embeddings and "
                                                                   "index them.")],
                      separator: Optional[str] = Form(NEWLINE, description="The separator to split your document in "
                                                                           "smaller chunks to be indexed."),
                      chunk_size: Optional[int] = Form(CHUNK_SIZE, description="After splitting `file` into chunks by "
                                                                               "using `separator`, we create small "
                                                                               "chunks of `chunk_size`."),
                      chunk_overlap: Optional[int] = Form(CHUNK_OVERLAP, description="In order to take context into "
                                                                                     "consideration, chunks also get a "
                                                                                     "surrounding context of a total of"
                                                                                     " `chunk_overlap` previous and "
                                                                                     "following characters.")
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
         a json response with fields: `message`, `code`, `result`
    """
    if file is None:
        return GenericSchema(message="File is None", result="", code=response_codes.EXCEPTION)
    if separator is None:
        separator = NEWLINE
    if chunk_size is None:
        chunk_size = CHUNK_SIZE
    if chunk_overlap is None:
        chunk_overlap = CHUNK_OVERLAP

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
        separator = separator.replace("\r", "")
        loader.index_pdf(contents, filename, separator, chunk_size, chunk_overlap)
        return GenericSchema(message=f"{filename} was successfully processed", result="",
                             code=response_codes.SUCCESS)

    except Exception as e:
        return GenericSchema(message=str(e), result="", code=response_codes.EXCEPTION)


@app.post("/process_text")
async def process_text(file: Annotated[UploadFile, Form(description="Your txt or pdf file to calculate embeddings and "
                                                                    "index them.")],
                       separator: Optional[str] = Form(NEWLINE, description="The separator to split your document in "
                                                                            "smaller chunks to be indexed."),
                       chunk_size: Optional[int] = Form(CHUNK_SIZE, description="After splitting `file` into chunks by "
                                                                                "using `separator`, we create small "
                                                                                "chunks of `chunk_size`"),
                       chunk_overlap: Optional[int] = Form(CHUNK_OVERLAP, description="In order to take context into "
                                                                                      "consideration, chunks also get a"
                                                                                      " surrounding context of a total "
                                                                                      "of `chunk_overlap` previous and "
                                                                                      "following characters.")):
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
          a json response with fields: `message`, `code`, `result`
     """
    if file is None:
        return GenericSchema(message="File is None", result="", code=response_codes.EXCEPTION)

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
        separator = separator.replace("\r", "")
        loader.index_text(contents, filename, separator, chunk_size, chunk_overlap)
        return GenericSchema(message=f"{filename} was successfully processed", result="",
                             code=response_codes.SUCCESS)

    except Exception as e:
        return GenericSchema(message=str(e), result="", code=response_codes.EXCEPTION)


@app.post("/query")
async def query(question: Annotated[str, Form(description="Question or query to retrieve information from"
                                                          "your vector store")],
                generate_answer: Optional[str] = Form(None, description="`True` if you want to generate an answer, "
                                                                        "`False` otherwise"),
                items: Optional[int] = Form(None, description="Number of items to retrieve"),
                use_mockup_answer: Optional[str] = Form(None, description="True if you want to return a mockup answer, "
                                                                          "False otherwise (testing purposes only)")):
    """
        This endpoint will trigger your Vector Store database looking for the min cosine distance towards all the chunks
        previously indexed.

    Args:\n\n
    - `question`: Question or query to retrieve information from your vector store
    - `generate_answer`: True if you want to generate an answer using the results. False otherwise.
    - `items`: Number of items to retrieve

    Returns:\n\n
        a json response with fields: `message`, `code`, `result`
    """
    logging.info(f"Triggering {question} towards the index")
    try:
        querier = Querier(loader)
        results = querier.retrieve(question, items)

        generate_answer = str(generate_answer).lower() == "true"

        contexted_answer = ""
        if generate_answer:
            generator = AnswerGenerator()

            relevant_results = [r.page_content.strip() for r, x in results if x <= RELEVANT_THRESHOLD]
            contexted_answer = NOT_ENOUGH_RESULTS_TO_GENERATE_ANSWER
            if len(relevant_results) > 0:
                if use_mockup_answer is not None and use_mockup_answer.lower() == "true":
                    contexted_answer = generator.generate_mock(question, relevant_results)
                else:
                    contexted_answer = generator.generate(question, relevant_results)

        main_result = {}

        dict_result = []
        for r, score in results:
            partial = {'answer': r.page_content.strip(),
                       'filename': r.metadata['uploaded_filename'],
                       'title': r.metadata['title'] if 'title' in r.metadata else '',
                       'author': r.metadata['author'] if 'author' in r.metadata else '',
                       'page_number': r.metadata['page_number'] if 'page_number' in r.metadata else '',
                       'total_pages': r.metadata['total_pages'] if 'total_pages' in r.metadata else '',
                       'distance': round(score, 2),
                       'is_relevant': score <= RELEVANT_THRESHOLD
                       }
            dict_result.append(partial)
        main_result['contexted_answer'] = contexted_answer.strip()
        main_result['answers'] = dict_result
        return GenericSchema(message=f"Processed: `{question}`", result=main_result,
                             code=response_codes.SUCCESS)

    except Exception as e:
        return GenericSchema(message=str(e), result="", code=response_codes.EXCEPTION)


if __name__ == "__main__":
    # loader.show_collection_data()
    uvicorn.run(app, host=HOST, port=PORT)
