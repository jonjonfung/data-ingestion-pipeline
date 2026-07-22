from aws_cdk import Stack, RemovalPolicy
from aws_cdk import aws_s3 as s3
from constructs import Construct


class EtoroPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        s3.Bucket(
            self,
            "EtoroPipelineBucket",
            bucket_name="etoro-pipeline-john",
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN,
        )
