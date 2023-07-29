FROM python:3.10.4-buster
WORKDIR /docai
ADD . /docai

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["bash", "entrypoint.sh"]
