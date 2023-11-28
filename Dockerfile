FROM python:3.12.0-alpine

USER 0

COPY ./src ./src
COPY ./tests ./tests
COPY pytest.ini pytest.ini
COPY requirements.txt requirements.txt
COPY setup.py setup.py

RUN pip install -r requirements.txt --no-cache-dir

RUN pip install --no-cache-dir -e .