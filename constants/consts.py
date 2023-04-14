# Server configuration
import os

HOST = os.environ['HOST'] if 'HOST' in os.environ else "0.0.0.0"
PORT = os.environ['PORT'] if 'PORT' in os.environ else 5000

# ChromaDB configuration
COLLECTION = os.environ['COLLECTION'] if 'COLLECTION' in os.environ else 'sintetic'
PERSIST_DIR = 'indexes'

# Tmp folder
TMP_DIR = 'tmp/'

# LangChain
CHUNK_SIZE = os.environ['CHUNK_SIZE'] if 'CHUNK_SIZE' in os.environ else 100
CHUNK_OVERLAP = os.environ['CHUNK_OVERLAP'] if 'CHUNK_OVERLAP' in os.environ else 50
NEWLINE = ".\n"
PARAGRAPH = "\n\n"

# To detect if a document has \n\n or just \n, I check how big are the splits by '\n\n'
AVG_SIZE_OF_PARAGRAPH = os.environ['AVG_SIZE_OF_PARAGRAPH'] if 'AVG_SIZE_OF_PARAGRAPH' in os.environ else 1000

RELEVANT_THRESHOLD = os.environ['RELEVANT_THRESHOLD'] if 'RELEVANT_THRESHOLD' in os.environ else 0.41

NOT_ENOUGH_RESULTS_TO_GENERATE_ANSWER = "(Not enough results to combine in a single answer)"

AUTHENTICATED = 0
