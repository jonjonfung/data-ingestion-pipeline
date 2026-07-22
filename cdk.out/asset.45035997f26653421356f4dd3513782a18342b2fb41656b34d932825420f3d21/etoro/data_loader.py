import json
import boto3
from datetime import datetime, timezone

BUCKET = "etoro-pipeline-john"
REGION = "ap-southeast-2"


def _s3():
    return boto3.client("s3", region_name=REGION)


def save_portfolio(data: dict):
    """
    Save portfolio snapshot to S3 as JSON, partitioned by date.
    s3://etoro-pipeline-john/portfolio/YYYY-MM-DD/snapshot.json
    """
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    key = f"portfolio/{date}/snapshot.json"

    _s3().put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(data, indent=2),
        ContentType="application/json",
    )

    print(f"Saved to s3://{BUCKET}/{key}")
