import boto3

import json

def WriteToDatabase(table: str, data: dict) -> None:

    print(f"Writing to table: {table}")
    print(data)

    dynamodb = boto3.resource('dynamodb', region='us-west-2')
    table = dynamodb.Table(table)

    table.put_item(
        Item = data
    )