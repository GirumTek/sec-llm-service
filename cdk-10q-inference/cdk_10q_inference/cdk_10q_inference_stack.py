from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam,
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