import sys
from time import sleep

import argparse
import requests
import logging
import copy
import json
from datetime import datetime

from botocore.client import ClientError
import boto3

CATEGORY_IDS = ["1", "5", "8", "71", "6001"]

def ingest_data(env, date, bucket):
    endpoint = f'https://geo.irceline.be/sos/api/v1/stations/'
    stations_data = requests.get(endpoint).json()
    station_ids = [x['properties']['id'] for x in stations_data]
    ts_count = 0
    logging.info(f"Found {len(station_ids)} stations to ingest data from.")
    
    for station_id in station_ids:
        endpoint = f'https://geo.irceline.be/sos/api/v1/stations/{station_id}?expanded=true'

        raw_data = requests.get(endpoint).json()
        raw_data['properties']['date'] = date
        time_series = raw_data['properties']['timeseries']

        # only keep timeseries ids which correspond to one of the interesting category ids
        filtered_tsi = [x for x in time_series.keys() if time_series[x]['category']['id'] in CATEGORY_IDS]
        
        
        for tsi in filtered_tsi:
            # get the values for a day of all these timeseries
            raw_timeseries_data = get_timeseries_of_date(tsi, date)

            # Add values to the timeseries field
            time_series[str(tsi)]['values'] = raw_timeseries_data

            raw_data_copy = copy.deepcopy(raw_data)
            raw_data_copy['properties']['timeseries'] = {}
            raw_data_copy['properties']['timeseries'][str(tsi)] = raw_data['properties']['timeseries'][str(tsi)]
            metric = raw_data_copy['properties']['timeseries'][str(tsi)]['category']['label']
            station = raw_data_copy['properties']['timeseries'][str(tsi)]['feature']['label']
            
            ts_count += 1
            bucket.put_object(Body=json.dumps(raw_data_copy), Key=f'Alec-data/{date}/{station}/{metric}.json', ContentType='application/json')
    logging.info(f'Ingested {ts_count} timeseries.')
    

def get_timeseries_of_date(timeseries_id, date):
    endpoint = f"https://geo.irceline.be/sos/api/v1/timeseries/{timeseries_id}/getData?timespan=PT23H/{date}"
    raw_timeseries_data = requests.get(endpoint).json()
    return raw_timeseries_data

def create_s3_if_not_exists(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    
    try:
        s3.meta.client.head_bucket(Bucket=bucket.name)
    except ClientError:
        logging.info(f'Creating S3 bucket named {bucket_name}')
        bucket = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})

    return bucket

def push_s3(raw_data):
    pass

def process_raw_data(s3_bucket: str, date: str):
    pass

def main():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    parser = argparse.ArgumentParser(description="Building greeter")
    parser.add_argument(
        "-d", "--date", dest="date", help="date in format YYYY-mm-dd", required=True
    )
    parser.add_argument(
        "-e", "--env", dest="env", help="The environment in which we execute the code", required=True
    )
    args = parser.parse_args()
    logging.info(f"Using args: {args}")

    bucket = create_s3_if_not_exists('data-track-integrated-exercise')
    ingest_data(args.env, args.date, bucket)

if __name__ == "__main__":
    main()