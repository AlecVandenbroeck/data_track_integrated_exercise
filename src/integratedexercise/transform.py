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

    list_of_files = [f"s3a://data-track-integrated-exercise/{x.key}" for x in bucket.objects.filter(Prefix=f'Alec-data/raw/{date}')]
    df = session.read.option("multiline", "true").json(list_of_files)

    df = df.drop('type')
    df = df.withColumn('coordinates', df.geometry.coordinates)
    df = df.drop('geometry')
    df = df.withColumn('coordinate_x', df.coordinates[0])
    df = df.withColumn('coordinate_y', df.coordinates[1])
    df = df.withColumn('coordinate_z', df.coordinates[2])
    df = df.drop('coordinates')
    df = df.withColumn('date', df.properties.date)
    df = df.withColumn('station_id', df.properties.id)
    df = df.withColumn('station_label', df.properties.label)
    df = df.withColumn('timeseries', df.properties.timeseries)
    df = df.drop('properties')
    df = df.withColumn('service_id', df.timeseries.service.id)
    df = df.withColumn('service_label', df.timeseries.service.label)
    df = df.withColumn('offering_id', df.timeseries.offering.id)
    df = df.withColumn('offering_label', df.timeseries.offering.label) 
    df = df.withColumn('feature_id', df.timeseries.feature.id)
    df = df.withColumn('feature_label', df.timeseries.feature.label)
    df = df.withColumn('procedure_id', df.timeseries.procedure.id)
    df = df.withColumn('procedure_label', df.timeseries.procedure.label) 
    df = df.withColumn('phenomenon_id', df.timeseries.phenomenon.id)
    df = df.withColumn('phenomenon_label', df.timeseries.phenomenon.label)
    df = df.withColumn('category_id', df.timeseries.category.id)
    df = df.withColumn('category_label', df.timeseries.category.label) 
    df = df.withColumn('measurements', explode(df.timeseries.values))
    df = df.drop('timeseries')
    df = df.withColumn('datetime', to_timestamp(df.measurements.timestamp/1000))
    df = df.withColumn('measurement_value', df.measurements.value)
    df = df.withColumn('measurement_timestamp', df.measurements.timestamp)
    df = df.drop('measurements')

    df.write.parquet(f"s3a://data-track-integrated-exercise/Alec-data/clean/{date}", partitionBy=['phenomenon_id', 'station_id'], mode='overwrite')
    logging.info(f"Total number of rows written: {df.count()}")
    return


def main():
    parser = argparse.ArgumentParser(description="Script to transform data from a specific date")
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
        bucket.upload_file(f'{args.date}.log', f'Alec-data/logs/{args.date}/transform.log')
        os.remove(f'{args.date}.log')

if __name__ == "__main__":
    main()