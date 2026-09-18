from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as integrations,
    aws_apigatewayv2_authorizers as authorizers,
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

        edge_fn = PythonFunction(
            self, "TenQEdgeFunction",
            entry="edge_lambda",
            index="app.py",
            handler="lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            timeout=Duration.seconds(25),
            memory_size=256,
            environment={
                "CORE_FUNCTION_NAME": inference_fn.function_name,
            },
        )

        edge_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["lambda:InvokeFunction"],
                resources=[inference_fn.function_arn],
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

        
        user_pool_id = "us-east-2_uqnEzF2Fl"
        user_pool_client_id = "5sagtah0tiqcnqfk8rr3rstu8u"

        authorizer = authorizers.HttpJwtAuthorizer(
            "CognitoAuthorizer",
            jwt_issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{user_pool_id}",
            jwt_audience=[user_pool_client_id],
        )

        http_api.add_routes(
            path="/inference",
            methods=[apigwv2.HttpMethod.POST],
            integration=integrations.HttpLambdaIntegration(
                "EdgeIntegration", edge_fn
            ),
            authorizer=authorizer,
        )

        CfnOutput(self, "ApiEndpoint", value=http_api.api_endpoint)