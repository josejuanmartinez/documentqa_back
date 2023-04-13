# Server configuration
HOST = "0.0.0.0"
PORT = 5000

# ChromaDB configuration
COLLECTION = "sintetic"
PERSIST_DIR = 'indexes'

# Tmp folder
TMP_DIR = 'tmp/'

# LangChain
CHUNK_SIZE = 100
CHUNK_OVERLAP = 50
NEWLINE = ".\n"
PARAGRAPH = "\n\n"

# To detect if a document has \n\n or just \n, I check how big are the splits by '\n\n'
AVG_SIZE_OF_PARAGRAPH = 1000

RELEVANT_THRESHOLD = 0.41

NOT_ENOUGH_RESULTS_TO_GENERATE_ANSWER = "(Not enough results to combine in a single answer)"

AUTHENTICATED = 0
