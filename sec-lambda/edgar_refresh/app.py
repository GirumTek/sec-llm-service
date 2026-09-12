import json
import os
import requests
import boto3

def lambda_handler(event, context):
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {
        "User-Agent": "Girum Tekle thegirumtekle@gmail.com"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    bucket_name = os.environ["BUCKET_NAME"]
    s3 = boto3.client("s3")

    s3.put_object(
        Bucket=bucket_name,
        Key="company_tickers.json",
        Body=response.content,
        ContentType="application/json"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "EDGAR refresh complete"})
    }