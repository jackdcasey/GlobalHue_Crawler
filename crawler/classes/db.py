import boto3

import logging

AWS_REGION = 'us-west-2'

def WriteToDatabase(table: str, data: dict) -> None:

    logging.info(f"Writing to table: {table}")
    logging.info(data)

    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(table)

    table.put_item(
        Item = data
    )