import sys
from time import sleep

import argparse
import requests
import logging

def process_raw_data(s3_bucket: str, date: str):
    station_id = 1163
    raw_data = requests.get('https://geo.irceline.be/sos/api/v1/stations/{station_id}?expanded=true')
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
    ingest_data(args.path, args.date)

if __name__ == "__main__":
    main()