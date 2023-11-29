FROM python:3.12.0

ADD ./src/integratedexercise/util.py .
ADD ./src/integratedexercise/ingest.py .
ADD requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir
CMD ["python","ingest.py","-d","2023-11-28","-e","all"]