FROM python:3.7
WORKDIR /docai
ADD . /docai

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["bash", "entrypoint.sh"]
