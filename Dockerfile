FROM python:3.9

EXPOSE 5000

RUN apt update

RUN mkdir -p /usr/src/sintetic.ai/qa/back

WORKDIR /usr/src/syntetic.ai/qa/back

COPY requirements.txt ./

RUN pip install -r requirements.txt

ADD . ./

CMD ["python", "main.py"]

