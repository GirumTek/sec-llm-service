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
    # 1. Validate
    question = event.get("question")
    ticker = event.get("ticker")
    year = event.get("year")
    period = event.get("period")

    if not question or not isinstance(question, str):
        return error_response("question", question, "must be a non-empty string")
    if not ticker or not isinstance(ticker, str) or not ticker.isupper():
        return error_response("ticker", ticker, "must be a non-empty string containing only uppercase letters")
    if not isinstance(year, int) or year < 1900:
        return error_response("year", year, "must be a four-digit integer (1900 or later)")
    if period not in VALID_PERIODS:
        return error_response("period", period, f"Must be one of: {', '.join(VALID_PERIODS)}.")

    # 2. Retrieve
    lookup = CIKLookup()
    result = lookup.ticker_to_cik(ticker)
    if result is None:
        return {"error": "NotFound", "message": f"No company found for ticker '{ticker}'"}

    cik = str(result[0])

    if period == "FY":
        doc_url = lookup.annual_filing(cik, year)
    else:
        quarter = int(period[1])
        doc_url = lookup.quarterly_filing(cik, year, quarter)

    if doc_url is None:
        return {"error": "NotFound", "message": f"No {period} filing found for {ticker} in {year}"}

    filing_response = requests.get(doc_url, headers=HEADERS)
    filing_response.raise_for_status()
    raw_html = filing_response.text

    # 3. Extract
    filing_text = extract_text(raw_html, MAX_CONTEXT_TOKENS)

    # 4. Invoke
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

    return {
        "answer": answer,
        "meta": {
            "model": MODEL_ID,
            "input_tokens": usage["inputTokens"],
            "output_tokens": usage["outputTokens"],
            "latency_ms": latency_ms,
        },
    }


def error_response(field, value, rule):
    return {
        "error": "ValidationError",
        "message": f"Invalid value for '{field}': '{value}'. {rule}"
    }