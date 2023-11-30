from airflow import DAG
from airflow.providers.amazon.aws.operators.batch import BatchOperator
from airflow.providers.amazon.aws.sensors.batch import BatchSensor
from airflow.operators.dummy import DummyOperator
from datetime import datetime as dt

main_dag = DAG(
    dag_id="ingest_pipeline_tf",
    description="Ingestion DAG",
    default_args={"owner": "Alec Van den broeck"},
    schedule_interval="@daily",
    start_date=dt(2023, 11, 22),
)

with main_dag:
    submit_ingest_job = BatchOperator(
        task_id="alec-ingest",
        job_name="alec-ingest",
        job_definition="dt-alec-ingest-tf",
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

    submit_transform_job = BatchOperator(
        task_id="alec-transform",
        job_name="alec-transform",
        job_definition="dt-alec-transform-tf",
        job_queue="integrated-exercise-job-queue",
        region_name="eu-west-1",
        overrides={"command": [
        "python3",
        "./transform.py",
        "-d",
        "{{ds}}"
        ]},
    )

    submit_egress_job = BatchOperator(
        task_id="alec-egress",
        job_name="alec-egress",
        job_definition="dt-alec-egress-tf",
        job_queue="integrated-exercise-job-queue",
        region_name="eu-west-1",
        overrides={"command": [
        "python3",
        "./egress.py",
        "-d",
        "{{ds}}"
        ]},
    )
    submit_ingest_job >> submit_transform_job >> submit_egress_job