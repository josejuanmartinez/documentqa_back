FROM python:3.9

RUN apt update

RUN mkdir /usr/src/sintetic.ai
RUN mkdir /usr/src/sintetic.ai/back
RUN mkdir /usr/src/sintetic.ai/front

WORKDIR /usr/src/syntetic.ai/back

COPY requirements.txt ./

RUN pip install -r requirements.txt

ADD . ./

CMD ["python", "main.py"]

