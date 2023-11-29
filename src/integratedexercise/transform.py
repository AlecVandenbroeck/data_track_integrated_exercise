import logging
import sys
import argparse
from util import create_s3_if_not_exists
import os
import boto3
from pyspark.sql import SparkSession

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

    list_of_files = [f"s3a://{x.key}" for x in bucket.objects.filter(Prefix='Alec-data/raw/')]
    print(list_of_files[:10])
    df = session.read.json(list_of_files[:10])
    df.show(10)

    #bucket = create_s3_if_not_exists('data-track-integrated-exercise')
    #bucket.put_object(Body='', Key=f'', ContentType='application/json')
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

        transform_raw_data(args.date, bucket)
    except Exception as e:
        logging.error(e)
    finally:
        bucket.upload_file(f'{args.date}.log', f'Alec-data/logs/{args.date}/transform.log')
        os.remove(f'{args.date}.log')

if __name__ == "__main__":
    main()