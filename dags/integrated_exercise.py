from airflow import DAG
from airflow.providers.amazon.aws.operators.batch import BatchOperator
from datetime import datetime as dt

ingest_dag = DAG(
    dag_id="ingest_pipeline",
    description="Ingestion DAG",
    default_args={"owner": "Alec Van den broeck"},
    schedule_interval="@daily",
    start_date=dt(2023, 11, 23),
)

with ingest_dag:
    ingest_task = BatchOperator(
        task_id="alec-ingest",
        job_name="alec-ingest",
        job_definition="dt-alec-ingest",
        job_queue="integrated-exercise-job-queue",
        region_name="eu-west-1",
        overrides={"command": [
        "python",
        "./ingest.py",
        "-d",
        "{{ds}}",
        "-e",
        "all"
        ]},
    )