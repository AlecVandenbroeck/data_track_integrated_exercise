FROM public.ecr.aws/dataminded/spark-k8s-glue:v3.2.1-hadoop-3.3.1

ENV PYSPARK_PYTHON python3
WORKDIR /opt/spark/work-dir

USER 0

ADD ./src/integratedexercise/util.py .
ADD ./src/integratedexercise/egress.py .
ADD requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

CMD ["python3","egress.py","-d","2023-11-28"]