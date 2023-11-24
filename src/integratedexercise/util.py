from botocore.client import ClientError
import boto3
import logging


def create_s3_if_not_exists(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    
    try:
        s3.meta.client.head_bucket(Bucket=bucket.name)
    except ClientError:
        logging.info(f'Creating S3 bucket named {bucket_name}')
        bucket = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})

    return bucket