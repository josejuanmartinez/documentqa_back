# Back for Document QA
Developed using python, FastAPI, LangChain, OpenAI api and Chroma as Vector Store.

## Running in dev
Set this env variables in the OS or in your IDE.
OPENAI_API_KEY=[YOUR_API_KEY];KEYRING_SECRET_KEY=[ANY_SECRET_KEYRING_KEYWORD]

Then, `python main.py`. You will need first to create a user for the login (check User Management).

## User management
To create a user and add it using keyring, just run in the console of the environment 
/ container the following:
```
cd users
python add_user.py -e [email] -p [password]
```
After that, you will be able to log in using [email] and [password]

## API documentation
To check the API documentation you have 2 endpoints:
- For SWAGGER documentation available at http://localhost:5000/docs
- For ReDOC, http://localhost:5000/redoc

## Dockerization
Example of a docker-compose to build an image of the back with the front and a 
healthchecker manager:
```
version: '3.3'

services:
  documentqa_back:
    image: documentqa_back_image
    build: ./documentqa_back
    container_name: documentqa_back
    volumes:
      - ./documentqa_back/.chroma:/usr/src/sintetic.ai/back/.chroma
      - ./documentqa_back/indexes:/usr/src/sintetic.ai/back/indexes
      - ./documentqa_back/tmp:/usr/src/sintetic.ai/back/tmp
    ports:
      - "5000:5000"
    restart: always
    environment:
      - OPENAI_API_KEY=[YOUR_API_KEY]
      - KEYRING_SECRET_KEY=[ANY_SECRET_KEYRING_KEYWORD]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/healthcheck"]
      interval: 12s
      timeout: 12s
      start_period: 40s
      retries: 5
    networks:
      - documentqa_network

  documentqa_front:
    image: documentqa_front_image
    build: ./documentqa_front
    container_name: documentqa_front
    ports:
      - "8080:80"
    restart: always
    depends_on:
      - documentqa_back
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/login"]
      interval: 12s
      timeout: 12s
      start_period: 40s
      retries: 5
    networks:
      - documentqa_network

  autoheal:
    restart: always
    image: willfarrell/autoheal
    environment:
      - AUTOHEAL_CONTAINER_LABEL=all
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - documentqa_network

networks:
  documentqa_network:
      name: documentqa_network
```
