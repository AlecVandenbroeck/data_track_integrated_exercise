import logging
import sys
import argparse
from util import create_s3_if_not_exists
import os
import boto3
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import explode, avg, to_timestamp
from datetime import datetime as dt
import json
from time import time

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
    SNOWFLAKE_SOURCE_NAME = "net.snowflake.spark.snowflake"
    session = SparkSession.builder.config(
        "spark.jars.packages",
        ",".join(
            [
                "org.apache.hadoop:hadoop-aws:3.3.1",
                "net.snowflake:spark-snowflake_2.12:2.5.4-spark_2.4",
                "net.snowflake:snowflake-jdbc:3.14.3"
            ]
        ),
    ).config(
        "fs.s3a.aws.credentials.provider",
        "com.amazonaws.auth.DefaultAWSCredentialsProviderChain",
    ).getOrCreate()
    sfOptions = get_snowflake_creds_from_sm('snowflake/integrated-exercise/alec-login')
    df = session.read.parquet(f"s3a://data-track-integrated-exercise/Alec-data/data-marts/aggregate_station_by_day/avg/{date}/")
    df = df.drop('date')
    

    
    session.sparkContext._jvm.net.snowflake.spark.snowflake.Utils.runQuery(sfOptions, 
                                                                          f"""CREATE TABLE IF NOT EXISTS ACADEMY_DBT.AXXES_ALEC.AVG_STATION_MEASUREMENT_{date.replace('-', '_')} (
                                                                            COORDINATE_X FLOAT, 
                                                                            COORDINATE_Y FLOAT, 
                                                                            STATION_LABEL VARCHAR,
                                                                            PHENOMENON_LABEL VARCHAR,
                                                                            DATETIME TIMESTAMP,
                                                                            AVERAGE_MEASUREMENT FLOAT,
                                                                            PHENOMENON_ID INTEGER,
                                                                            STATION_ID INTEGER)""")

    df.write.format(SNOWFLAKE_SOURCE_NAME).options(**sfOptions).option("dbtable", f"ACADEMY_DBT.AXXES_ALEC.AVG_STATION_MEASUREMENT_{date.replace('-', '_')}").mode('overwrite').options(header=True).save()
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
        start = time()
        egress_data(args.date, bucket)
        logging.info(f"Job succeeded in {(time()-start):.2f} seconds")
    except Exception as e:
        logging.error(e)
        logging.info(f"Job failed after {(time()-start):.2f} seconds")
        raise e
    finally:
        bucket.upload_file(f'{args.date}.log', f'Alec-data/logs/{args.date}/egress.log')
        os.remove(f'{args.date}.log')

if __name__ == "__main__":
    main()