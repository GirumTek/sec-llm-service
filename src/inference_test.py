import boto3
import json
import requests
import re

MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
bedrock = boto3.client("bedrock-runtime")

# --- Part 1: no context ---
request_body_1 = {"anthropic_version":"bedrock-2023-05-31",
                "max_tokens":500,
                "messages":[{"role":"user",
                "content":"What was Apple's total net sales for the fiscal quarter ended June 27, 2026?"}]}

response_1 = bedrock.invoke_model(modelId=MODEL_ID,contentType="application/json",accept="application/json", body = json.dumps(request_body_1))

response_body_1 = json.loads(response_1["body"].read())

print("PART 1 (no context):")
print(response_body_1["content"][0]["text"])

# --- fetch and clean the filing ---
url = "https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/aapl-20260627.htm"
headers = {
        "User-Agent": "Girum Tekle thegirumtekle@gmail.com"
    }

filing_response = requests.get(url, headers=headers)
html_content = filing_response.text

cleaned_content = re.sub("<.*?>", "", html_content)

prompt = f"Using the information below, answer the following question.\n\nQuestion: What was Apple's total net sales for the fiscal quarter ended June 27, 2026?\n\nDocument: {cleaned_content}"

# --- Part 2: with context ---
request_body_2 = {"anthropic_version":"bedrock-2023-05-31",
                "max_tokens":500,
                "messages":[{"role":"user",
                "content":prompt}]}

response_2 = bedrock.invoke_model(modelId=MODEL_ID,contentType="application/json",accept="application/json", body = json.dumps(request_body_2))

response_body_2 = json.loads(response_2["body"].read())

print("\nPART 2 (with context):")
print(response_body_2["content"][0]["text"])