FROM python:3.10
WORKDIR /docai
COPY . /docai

RUN pip install -r requirements.txt


# ENTRYPOINT ["bash", "entrypoint.sh"]
