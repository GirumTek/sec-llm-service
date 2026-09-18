from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as integrations,
    CfnOutput,
)
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from constructs import Construct


class Cdk10QInferenceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        inference_fn = PythonFunction(
            self, "TenQInferenceFunction",
            entry="lambda",
            index="app.py",
            handler="lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            timeout=Duration.seconds(60),
            memory_size=512,
        )

        inference_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=["*"],
            )
        )

        http_api = apigwv2.HttpApi(
            self, "TenQInferenceApi",
            cors_preflight=apigwv2.CorsPreflightOptions(
                allow_origins=["http://localhost:5173"],
                allow_methods=[apigwv2.CorsHttpMethod.POST, apigwv2.CorsHttpMethod.OPTIONS],
                allow_headers=["Content-Type", "Authorization"],
            ),
        )

        http_api.add_routes(
            path="/inference",
            methods=[apigwv2.HttpMethod.POST],
            integration=integrations.HttpLambdaIntegration(
                "InferenceIntegration", inference_fn
            ),
        )

        CfnOutput(self, "ApiEndpoint", value=http_api.api_endpoint)