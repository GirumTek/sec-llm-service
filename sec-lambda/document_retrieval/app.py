import json
from cik_lookup import CIKLookup

VALID_PERIODS = ["Q1", "Q2", "Q3", "Q4", "FY"]

def lambda_handler(event, context):
    # 1. Validate the request against the contract
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

    # 2. Look up the CIK for this ticker
    lookup = CIKLookup()
    result = lookup.ticker_to_cik(ticker)

    if result is None:
        return {
            "error": "NotFound",
            "message": f"No company found for ticker '{ticker}'"
        }


    cik = str(result[0])

    if period == "FY":
        doc_url = lookup.annual_filing(cik, year)
    else:
        quarter = int(period[1])  # "Q2" -> 2
        doc_url = lookup.quarterly_filing(cik, year, quarter)

   
    return {
        "answer": f"Filing found: {doc_url}",
        "meta": {
            "model": "not yet implemented",
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_ms": 0
        }
    }

def error_response(field, value, rule):
    return {
        "error": "ValidationError",
        "message": f"Invalid value for '{field}': '{value}'. {rule}"
    }