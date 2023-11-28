from airflow import DAG
from airflow.providers.amazon.aws.operators.batch import BatchOperator

ingest_dag = DAG(

)

ingest_task = BatchOperator(
    
)
