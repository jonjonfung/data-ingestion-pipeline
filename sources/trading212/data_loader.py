import json
import boto3
from datetime import datetime, timezone

BUCKET = "trading212-pipeline-john"
REGION = "ap-southeast-2"


def _s3():
    return boto3.client("s3", region_name=REGION)


def save_portfolio(data: dict):
    """
    Save portfolio snapshot two ways:
    1. Full JSON snapshot: s3://trading212-pipeline-john/portfolio/YYYY-MM-DD/snapshot.json
    2. JSONL positions:    s3://trading212-pipeline-john/positions/date=YYYY-MM-DD/data.jsonl
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
            "ticker": p.get("ticker"),
            "name": p.get("name"),
            "quantity": p.get("quantity"),
            "avg_price": p.get("avg_price"),
            "current_price": p.get("current_price"),
            "value": p.get("value"),
            "ppl": p.get("ppl"),
            "fx_ppl": p.get("fx_ppl"),
            "initial_fill_date": p.get("initial_fill_date"),
            "date": date,
        }))

    s3.put_object(
        Bucket=BUCKET,
        Key=f"positions/date={date}/data.jsonl",
        Body="\n".join(lines),
        ContentType="application/x-ndjson",
    )

    print(f"Saved snapshot and {len(lines)} positions to s3://{BUCKET}/")


def save_orders(orders: list[dict]):
    """
    Save full order history as JSONL for Athena.
    s3://trading212-pipeline-john/orders/data.jsonl
    (Overwritten on each run — full refresh, not partitioned)
    """
    s3 = _s3()
    lines = [json.dumps(o) for o in orders]
    s3.put_object(
        Bucket=BUCKET,
        Key="orders/data.jsonl",
        Body="\n".join(lines),
        ContentType="application/x-ndjson",
    )
    print(f"Saved {len(lines)} orders to s3://{BUCKET}/orders/data.jsonl")
