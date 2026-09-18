import os
import boto3
import json

lambda_client = boto3.client("lambda")



def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return respond(400, {"error": "ValidationError", "message": "Request body must be valid JSON."})

    required_fields = ["question", "ticker", "year", "period"]
        
    missing = []

    required_fields = ["question", "ticker", "year", "period"]

    for field in required_fields:
        if not body.get(field):
            missing.append(field)
            
    if missing:
        return respond(400, {"error": "ValidationError", "message": f"Missing required fields: {', '.join(missing)}"})

    payload = {"body": json.dumps(body)}

    response = lambda_client.invoke(
        FunctionName=os.environ["CORE_FUNCTION_NAME"],
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode(),
    )
    
    payload_bytes = response["Payload"].read()
    result = json.loads(payload_bytes)

    if "FunctionError" in response:
        return respond(502, {"error": "UpstreamError", "message": "Core Lambda failed", "details": result})

    return result

def respond(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body_dict)
    }
