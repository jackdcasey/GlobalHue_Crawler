import boto3

AWS_REGION = 'us-west-2'

def WriteToDatabase(table: str, data: dict) -> None:

    print(f"Writing to table: {table}")
    print(data)

    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(table)

    table.put_item(
        Item = data
    )