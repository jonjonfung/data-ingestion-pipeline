from aws_cdk import Stack, RemovalPolicy, Duration, BundlingOptions
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_iam as iam
from constructs import Construct


class EtoroPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket — stores weekly portfolio snapshots
        bucket = s3.Bucket(
            self, "EtoroBucket",
            bucket_name="etoro-pipeline-john",
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Lambda — runs the ingestion
        fn = lambda_.Function(
            self, "EtoroIngestFn",
            function_name="etoro-ingest",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="lambda_handler.main",
            code=lambda_.Code.from_asset(
                ".",
                exclude=["venv", ".git", "**/__pycache__", "**/*.pyc", ".env", "tests", "infra", "app.py", "cdk.json"],
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install requests -t /asset-output && cp -au . /asset-output",
                    ],
                ),
            ),
            environment={"S3_BUCKET": bucket.bucket_name},
            timeout=Duration.seconds(30),
            memory_size=128,
        )

        # Grant Lambda write access to S3
        bucket.grant_write(fn)

        # Grant Lambda read access to SSM secrets
        fn.add_to_role_policy(iam.PolicyStatement(
            actions=["ssm:GetParameter"],
            resources=["arn:aws:ssm:ap-southeast-2:*:parameter/etoro/*"],
        ))

        # EventBridge — triggers Lambda every Monday at 1am UTC
        rule = events.Rule(
            self, "WeeklySchedule",
            schedule=events.Schedule.cron(minute="0", hour="1", week_day="MON"),
        )
        rule.add_target(targets.LambdaFunction(fn))
