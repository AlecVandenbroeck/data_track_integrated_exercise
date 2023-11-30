import logging
import sys
import argparse
from util import create_s3_if_not_exists
import os
import boto3
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import explode, avg, to_timestamp
from datetime import datetime as dt

# https://community.snowflake.com/s/article/How-to-UPDATE-a-table-using-pyspark-via-the-Snowflake-Spark-connector

def get_snowflake_creds_from_sm(secret_name: str):
    sess = boto3.Session(region_name="eu-west-1")
    client = sess.client('secretsmanager')

    response = client.get_secret_value(
        SecretId=secret_name
    )

    creds = json.loads(response['SecretString'])
    return {
        "sfURL": f"{creds['URL']}",
        "sfPassword": creds["PASSWORD"],
        "sfUser": creds["USER_NAME"],
        "sfDatabase": creds["DATABASE"],
        "sfWarehouse": creds["WAREHOUSE"],
        "sfRole": creds["ROLE"]
    }

def egress_data(date: str, bucket):
    session = SparkSession.builder.config(
        "spark.jars.packages",
        ",".join(
            [
                "org.apache.hadoop:hadoop-aws:3.3.1",
                "net.snowflake:spark-snowflake_2.12:2.9.0-spark_3.1",
                "net.snowflake:snowflake-jdbc:3.13.3"
            ]
        ),
    ).config(
        "fs.s3a.aws.credentials.provider",
        "com.amazonaws.auth.DefaultAWSCredentialsProviderChain",
    ).getOrCreate()

    list_of_files = [f"s3a://data-track-integrated-exercise/{x.key}" for x in bucket.objects.filter(Prefix=f'Alec-data/clean/')]
    df = session.read.parquet(list_of_files)

    Utils.runQuery(sfOptions, "CREATE TABLE MY_TABLE(A INTEGER)")

    SNOWFLAKE_SOURCE_NAME = "net.snowflake.spark.snowflake"

    df = spark.write.format(SNOWFLAKE_SOURCE_NAME) \
    .options(**get_snowflake_creds_from_sm('snowflake/integrated-exercise/alec-login')) \
    .option("query",  "select 1 as my_num union all select 2 as my_num") \
    .option("dbtable", "emp_dept") \
    .mode("append").options(header=True).save()

    
    return


def main():
    parser = argparse.ArgumentParser(description="Script to egress data")
    parser.add_argument(
        "-d", "--date", dest="date", help="date in format YYYY-mm-dd", required=True
    )
    args = parser.parse_args()
    bucket = create_s3_if_not_exists('data-track-integrated-exercise')

    logging.basicConfig(filename=f'{args.date}.log', filemode='w+', level=logging.INFO, format='[%(levelname)s %(asctime)s] %(message)s')
    try:
        logging.info(f"Using args: {args}")

        egress_data(args.date, bucket)
    except Exception as e:
        logging.error(e)
        raise e
    finally:
        bucket.upload_file(f'{args.date}.log', f'Alec-data/logs/{args.date}/egress.log')
        os.remove(f'{args.date}.log')

if __name__ == "__main__":
    main()