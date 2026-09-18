import json
import time
import boto3
import requests
from cik_lookup import CIKLookup
from text_extraction import extract_text

MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
VALID_PERIODS = ["Q1", "Q2", "Q3", "Q4", "FY"]
MAX_CONTEXT_TOKENS = 160000 
HEADERS = {"User-Agent": "Girum Tekle thegirumtekle@gmail.com"}


def lambda_handler(event, context):

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return respond(400, {"error": "ValidationError", "message": "Request body must be valid JSON."})

    question = body.get("question")
    ticker = body.get("ticker")
    year = body.get("year")
    period = body.get("period")

    if not question or not isinstance(question, str):
        return respond(400, error_response("question", question, "must be a non-empty string"))
    if not ticker or not isinstance(ticker, str) or not ticker.isupper():
        return respond(400, error_response("ticker", ticker, "must be a non-empty string containing only uppercase letters"))
    if not isinstance(year, int) or year < 1900:
        return respond(400, error_response("year", year, "must be a four-digit integer (1900 or later)"))
    if period not in VALID_PERIODS:
        return respond(400, error_response("period", period, f"Must be one of: {', '.join(VALID_PERIODS)}."))

    
    lookup = CIKLookup()
    result = lookup.ticker_to_cik(ticker)
    if result is None:
        return respond(404, {"error": "NotFound", "message": f"No company found for ticker '{ticker}'"})

    cik = str(result[0])

    if period == "FY":
        doc_url = lookup.annual_filing(cik, year)
    else:
        quarter = int(period[1])
        doc_url = lookup.quarterly_filing(cik, year, quarter)

    if doc_url is None:
        return respond(404, {"error": "NotFound", "message": f"No {period} filing found for {ticker} in {year}"})
    try:
        filing_response = requests.get(doc_url, headers=HEADERS)
        filing_response.raise_for_status()
        raw_html = filing_response.text

    
        filing_text = extract_text(raw_html, MAX_CONTEXT_TOKENS)

    
        prompt = (
            f"Using only the SEC filing text provided below, answer the following question. "
            f"If the answer is not contained in the filing, say so explicitly.\n\n"
            f"Question: {question}\n\n"
            f"Filing ({ticker} {period} {year}):\n{filing_text}"
        )

        bedrock = boto3.client("bedrock-runtime")

        start = time.perf_counter()
        converse_response = bedrock.converse(
            modelId=MODEL_ID,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 1000},
        )
        latency_ms = int((time.perf_counter() - start) * 1000)

        answer = converse_response["output"]["message"]["content"][0]["text"]
        usage = converse_response["usage"]

        return respond(200, {
            "answer": answer,
            "meta": {
                "model": MODEL_ID,
                "input_tokens": usage["inputTokens"],
                "output_tokens": usage["outputTokens"],
                "latency_ms": latency_ms,
            },
        })

    except Exception as e:
        return respond(500, {"error": "InternalError", "message": str(e)})  


def error_response(field, value, rule):
    return {
        "error": "ValidationError",
        "message": f"Invalid value for '{field}': '{value}'. {rule}"
    }

def respond(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body_dict)
    }