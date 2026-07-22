import json
import boto3
from datetime import datetime, timezone

BUCKET = "etoro-pipeline-john"
REGION = "ap-southeast-2"


def _s3():
    return boto3.client("s3", region_name=REGION)


def save_portfolio(data: dict):
    """
    Save portfolio snapshot two ways:
    1. Full JSON snapshot: s3://etoro-pipeline-john/portfolio/YYYY-MM-DD/snapshot.json
    2. JSONL positions:    s3://etoro-pipeline-john/positions/date=YYYY-MM-DD/data.jsonl
       (Hive-partitioned so Athena can query it)
    """
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    s3 = _s3()

    # Full snapshot
    s3.put_object(
        Bucket=BUCKET,
        Key=f"portfolio/{date}/snapshot.json",
        Body=json.dumps(data, indent=2),
        ContentType="application/json",
    )

    # Positions as JSONL for Athena
    lines = []
    for p in data.get("positions", []):
        lines.append(json.dumps({
            "instrument_id": p.get("instrument_id"),
            "amount": p.get("amount"),
            "unrealized_pnl": p.get("unrealized_pnl"),
            "mirror_id": p.get("mirror_id"),
            "date": date,
        }))

    s3.put_object(
        Bucket=BUCKET,
        Key=f"positions/date={date}/data.jsonl",
        Body="\n".join(lines),
        ContentType="application/x-ndjson",
    )

    print(f"Saved snapshot and {len(lines)} positions to s3://{BUCKET}/")
