import sys
from time import sleep

import argparse
import requests
import logging
import copy
import json
import os
from datetime import datetime

from util import create_s3_if_not_exists

def ingest_data(date, bucket):
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

        filtered_tsi = time_series.keys()
        
        for tsi in filtered_tsi:
            # get the values for a day of all these timeseries
            raw_timeseries_data = get_timeseries_of_date(tsi, date)

            # Add values to the timeseries field
            time_series[str(tsi)]['values'] = raw_timeseries_data['values']

            raw_data_copy = copy.deepcopy(raw_data)
            raw_data_copy['properties']['timeseries'] = {}
            raw_data_copy['properties']['timeseries'] = raw_data['properties']['timeseries'][str(tsi)]
            metric = raw_data_copy['properties']['timeseries']['category']['id']
            station = raw_data_copy['properties']['timeseries']['feature']['id']
            
            ts_count += 1
            if ts_count == 1:
                print(json.dumps(raw_data_copy, indent=2))
            bucket.put_object(Body=json.dumps(raw_data_copy), Key=f'Alec-data/raw/{date}/{station}/{metric}.json', ContentType='application/json')
    
    logging.info(f'Ingested {ts_count} timeseries.')
    

def get_timeseries_of_date(timeseries_id, date):
    endpoint = f"https://geo.irceline.be/sos/api/v1/timeseries/{timeseries_id}/getData?timespan=PT23H/{date}"
    raw_timeseries_data = requests.get(endpoint).json()
    return raw_timeseries_data

def main():
    parser = argparse.ArgumentParser(description="Building greeter")
    parser.add_argument(
        "-d", "--date", dest="date", help="Date in format YYYY-mm-dd", required=True
    )
    parser.add_argument(
        "-e", "--env", dest="env", help="The environment in which we execute the code", required=True
    )
    args = parser.parse_args()
    bucket = create_s3_if_not_exists('data-track-integrated-exercise')
    
    logging.basicConfig(filename=f'{args.date}.log', filemode='w+', level=logging.INFO, format='[%(levelname)s %(asctime)s] %(message)s')
    try:
        logging.info(f"Using args: {args}")

        ingest_data(args.date, bucket)
    except Exception as e:
        logging.error(e)
        raise e
    finally:
        bucket.upload_file(f'{args.date}.log', f'Alec-data/logs/{args.date}/ingest.log')
        os.remove(f'{args.date}.log')
        
if __name__ == "__main__":
    main()