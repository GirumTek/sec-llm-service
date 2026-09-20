# SEC LLM Service

A full-stack service that answers natural-language questions about public companies' SEC filings (10-Q, 10-K), using live SEC EDGAR data and AWS Bedrock (Claude) for inference. Built as a self-study project covering the AWS serverless stack end to end: Lambda, CDK, API Gateway, Cognito, and Bedrock, with a React/TypeScript frontend.

## What it does

Given a company ticker, a filing period (quarter or fiscal year), and a question, the service:

1. Resolves the ticker to a CIK (SEC's company identifier) and looks up the correct filing via the EDGAR API
2. Downloads the filing and extracts clean, readable text from the raw HTML (stripping scripts, styles, and XBRL metadata)
3. Sends the question and filing text to Claude via AWS Bedrock
4. Returns a grounded answer, citing figures directly from the filing

## Architecture

Browser (React + Amplify Auth)
POST /inference, Authorization: Cognito ID token
API Gateway (HTTP API)
JWT Authorizer verifies token
Edge Lambda: validates request shape, invokes Core Lambda
Core Lambda: resolves filing, extracts text, calls Bedrock
AWS Bedrock (Claude Sonnet 4.5): answers from filing context

A separate scheduled Lambda refreshes SEC's company ticker list daily into a versioned S3 bucket.

## Repository structure

sec-llm-service/
- src/ : Core Python library, reused across Lambdas
  - cik_lookup.py : CIKLookup class, ticker/name to CIK, filing URL lookup
  - text_extraction.py : HTML to clean, token-budgeted plain text
- sec-lambda/ : SAM-deployed Lambda pair (initial deployment)
  - edgar_refresh/ : Daily scheduled job, refreshes ticker data into S3
  - document_retrieval/ : On-demand filing lookup and validation
- cdk-10q-inference/ : CDK-deployed inference stack (current architecture)
  - lambda/ : Core inference Lambda (retrieve, extract, invoke Bedrock)
  - edge_lambda/ : Edge Lambda, request validation and auth-aware delegation
  - cdk_10q_inference/ : CDK stack definition (API Gateway, Cognito authorizer, IAM)
- girumtek-partner-bot/ : React and TypeScript frontend (Amplify Gen 2)
  - src/ChatForm.tsx : Query form, calls the API, renders Markdown answers
  - src/main.tsx : Amplify configuration, Authenticator wrapper

## Tech stack

- Backend: Python 3.12, AWS Lambda, AWS CDK (Python), AWS SAM
- AI/Inference: AWS Bedrock, Claude Sonnet 4.5 (Converse and InvokeModel APIs)
- Data: SEC EDGAR API (live company filings)
- API layer: API Gateway HTTP API, Lambda proxy integration, JWT authorizer
- Auth: Amazon Cognito (User Pool, Identity Pool)
- Frontend: React, TypeScript, Vite, AWS Amplify Gen 2, Amplify UI React
