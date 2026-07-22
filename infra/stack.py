import os
from aws_cdk import Stack, RemovalPolicy, Duration
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_glue as glue
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
                exclude=[
                    "venv", ".git", "cdk.out", "tests", "infra",
                    "**/__pycache__", "**/*.pyc", ".env",
                    "app.py", "cdk.json", "requirements.txt", "README.md",
                ],
            ),
            environment={
                "S3_BUCKET": bucket.bucket_name,
                "ETORO_PUBLIC_KEY": os.environ["ETORO_PUBLIC_KEY"],
                "ETORO_PRIVATE_KEY": os.environ["ETORO_PRIVATE_KEY"],
            },
            timeout=Duration.seconds(30),
            memory_size=128,
        )

        # Grant Lambda write access to S3
        bucket.grant_write(fn)

        # EventBridge — triggers Lambda every Monday at 1am UTC
        rule = events.Rule(
            self, "WeeklySchedule",
            schedule=events.Schedule.cron(minute="0", hour="1", week_day="MON"),
        )
        rule.add_target(targets.LambdaFunction(fn))

        # Glue database
        database = glue.CfnDatabase(
            self, "EtoroDB",
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name="etoro_db",
                description="eToro portfolio data",
            ),
        )

        # Glue table — positions (queryable via Athena)
        # Glue table — instruments reference (name, symbol, type)
        glue.CfnTable(
            self, "InstrumentsTable",
            catalog_id=self.account,
            database_name="etoro_db",
            table_input=glue.CfnTable.TableInputProperty(
                name="instruments",
                description="eToro instrument metadata (name, symbol, type)",
                table_type="EXTERNAL_TABLE",
                parameters={"classification": "json"},
                storage_descriptor=glue.CfnTable.StorageDescriptorProperty(
                    location="s3://etoro-pipeline-john/instruments/",
                    input_format="org.apache.hadoop.mapred.TextInputFormat",
                    output_format="org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                    serde_info=glue.CfnTable.SerdeInfoProperty(
                        serialization_library="org.openx.data.jsonserde.JsonSerDe",
                    ),
                    columns=[
                        glue.CfnTable.ColumnProperty(name="instrument_id", type="int"),
                        glue.CfnTable.ColumnProperty(name="name", type="string"),
                        glue.CfnTable.ColumnProperty(name="symbol", type="string"),
                        glue.CfnTable.ColumnProperty(name="type_id", type="int"),
                    ],
                ),
            ),
        ).add_dependency(database)

        # Glue table — closed trades history
        glue.CfnTable(
            self, "TradesTable",
            catalog_id=self.account,
            database_name="etoro_db",
            table_input=glue.CfnTable.TableInputProperty(
                name="trades",
                description="eToro closed trade history",
                table_type="EXTERNAL_TABLE",
                parameters={"classification": "json"},
                storage_descriptor=glue.CfnTable.StorageDescriptorProperty(
                    location="s3://etoro-pipeline-john/trades/",
                    input_format="org.apache.hadoop.mapred.TextInputFormat",
                    output_format="org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                    serde_info=glue.CfnTable.SerdeInfoProperty(
                        serialization_library="org.openx.data.jsonserde.JsonSerDe",
                    ),
                    columns=[
                        glue.CfnTable.ColumnProperty(name="trade_id", type="bigint"),
                        glue.CfnTable.ColumnProperty(name="instrument_id", type="int"),
                        glue.CfnTable.ColumnProperty(name="is_buy", type="boolean"),
                        glue.CfnTable.ColumnProperty(name="open_date", type="string"),
                        glue.CfnTable.ColumnProperty(name="close_date", type="string"),
                        glue.CfnTable.ColumnProperty(name="investment", type="double"),
                        glue.CfnTable.ColumnProperty(name="net_profit", type="double"),
                        glue.CfnTable.ColumnProperty(name="open_rate", type="double"),
                        glue.CfnTable.ColumnProperty(name="close_rate", type="double"),
                        glue.CfnTable.ColumnProperty(name="fees", type="double"),
                        glue.CfnTable.ColumnProperty(name="leverage", type="int"),
                    ],
                ),
            ),
        ).add_dependency(database)

        glue.CfnTable(
            self, "PositionsTable",
            catalog_id=self.account,
            database_name="etoro_db",
            table_input=glue.CfnTable.TableInputProperty(
                name="positions",
                description="Weekly eToro position snapshots",
                table_type="EXTERNAL_TABLE",
                parameters={"classification": "json"},
                partition_keys=[
                    glue.CfnTable.ColumnProperty(name="date", type="string")
                ],
                storage_descriptor=glue.CfnTable.StorageDescriptorProperty(
                    location=f"s3://etoro-pipeline-john/positions/",
                    input_format="org.apache.hadoop.mapred.TextInputFormat",
                    output_format="org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                    serde_info=glue.CfnTable.SerdeInfoProperty(
                        serialization_library="org.openx.data.jsonserde.JsonSerDe",
                    ),
                    columns=[
                        glue.CfnTable.ColumnProperty(name="instrument_id", type="int"),
                        glue.CfnTable.ColumnProperty(name="amount", type="double"),
                        glue.CfnTable.ColumnProperty(name="unrealized_pnl", type="double"),
                        glue.CfnTable.ColumnProperty(name="mirror_id", type="string"),
                    ],
                ),
            ),
        ).add_dependency(database)
