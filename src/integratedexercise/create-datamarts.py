import logging
import sys
import argparse
from util import create_s3_if_not_exists
import os
import boto3
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import explode, avg, to_timestamp
from datetime import datetime as dt
from time import time

def transform_raw_data(date: str, bucket):
    session = SparkSession.builder.config(
        "spark.jars.packages",
        ",".join(
            [
                "org.apache.hadoop:hadoop-aws:3.3.1",
            ]
        ),
    ).config(
        "fs.s3a.aws.credentials.provider",
        "com.amazonaws.auth.DefaultAWSCredentialsProviderChain",
    ).getOrCreate()

    df = session.read.parquet(f"s3a://data-track-integrated-exercise/Alec-data/clean/{date}/")

    df = df.drop('coordinate_z', 'category_id', 'category_label', 'procedure_id', 'procedure_label', 'feature_id', 'feature_label', 'service_id', 'service_label', 'offering_id', 'offering_label')
    df = df.groupBy('phenomenon_id', 'phenomenon_label', 'coordinate_x', 'coordinate_y', 'station_label', 'station_id').agg(avg('measurement_value').alias('average_measurement'))
    df = df.drop('measurement_value', 'measurement_timestamp')

    df.write.parquet(f"s3a://data-track-integrated-exercise/Alec-data/data-marts/aggregate_station_by_day/avg/{date}", partitionBy=['phenomenon_id', 'station_id'], mode='overwrite')
    logging.info(f"Total number of rows written: {df.count()}")
    return


def main():
    parser = argparse.ArgumentParser(description="Script to create datamarts for a specific date")
    parser.add_argument(
        "-d", "--date", dest="date", help="date in format YYYY-mm-dd", required=True
    )
    args = parser.parse_args()
    bucket = create_s3_if_not_exists('data-track-integrated-exercise')

    logging.basicConfig(filename=f'{args.date}.log', filemode='w+', level=logging.INFO, format='[%(levelname)s %(asctime)s] %(message)s')
    try:
        logging.info(f"Using args: {args}")
        start = time()
        transform_raw_data(args.date, bucket)
        logging.info(f"Job succeeded in {(time()-start):.2f} seconds")
    except Exception as e:
        logging.error(e)
        logging.info(f"Job failed after {(time()-start):.2f} seconds")
        raise e
    finally:
        bucket.upload_file(f'{args.date}.log', f'Alec-data/logs/{args.date}/create-datamarts.log')
        os.remove(f'{args.date}.log')

if __name__ == "__main__":
    main()