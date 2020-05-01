import boto3

import logging, os

AWS_REGION = 'us-west-2'

def getFileFromS3(bucket: str, filename: str) -> str:

    logging.info(F"Downloading {filename} from {bucket}")

    s3 = boto3.resource('s3', region_name=AWS_REGION)

    obj = s3.Object(bucket, filename)
    return obj.get()['Body'].read().decode('utf-8')