FROM python:3.9-slim-buster

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /code/src
RUN mkdir -p /code/tests

COPY src/ /code/src/
COPY tests/ /code/tests/

WORKDIR /code
ENV FLASK_APP=src/allocation/entrypoints/flask_app.py FLASK_DEBUG=1 PYTHONUNBUFFERED=1
CMD flask run --host=0.0.0.0 --port=80