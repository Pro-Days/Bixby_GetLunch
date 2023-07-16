import json
import boto3

client = boto3.resource("dynamodb")
table = client.Table("Menu")


def lambda_handler(event, context):
    if "queryStringParameters" in event:
        date = event["queryStringParameters"]["date"]
    else:
        date = "오늘"

    try:
        response = table.get_item(Key={"date": date})
        item = response["Item"]
    except KeyError as err:
        print(err)
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps("급식 정보를 불러올 수 없습니다."),
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(item, indent=4),
    }
