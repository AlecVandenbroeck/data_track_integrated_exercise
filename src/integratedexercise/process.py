import logging
import sys
import argparse
from util import create_s3_if_not_exists
import json
import boto3
from pyspark.sql import SparkSession

def process_raw_data(date: str):
    SparkSession.builder.config(
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

    bucket = create_s3_if_not_exists('data-track-integrated-exercise')
    bucket.put_object(Body='', Key=f'', ContentType='application/json')
    pass


def main():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    parser = argparse.ArgumentParser(description="Script to transform data from a specific date")
    parser.add_argument(
        "-d", "--date", dest="date", help="date in format YYYY-mm-dd", required=True
    )
    args = parser.parse_args()
    logging.info(f"Using args: {args}")

    process_raw_data(args.date)

if __name__ == "__main__":
    main()