import json
import boto3
from .api_client import get

BUCKET = "trading212-pipeline-john"
REGION = "ap-southeast-2"


def fetch_dividends() -> list[dict]:
    """Fetch full dividend history from Trading212 (cursor-paginated)."""
    dividends = []
    path = "/api/v0/equity/history/dividends?limit=50"

    while path:
        data = get(path)
        for d in data.get("items", []):
            raw_ticker = d.get("ticker", "")
            dividends.append({
                "ticker": raw_ticker.split("_")[0],
                "name": d.get("instrument", {}).get("name"),
                "amount": d.get("amount", 0),
                "gross_amount_per_share": d.get("grossAmountPerShare", 0),
                "quantity": d.get("quantity", 0),
                "date_received": d.get("dateReceived", "")[:10],
                "type": d.get("type", ""),
            })
        path = data.get("nextPagePath")

    return dividends


def save_dividends(dividends: list[dict]):
    """Save all dividends to S3 as JSONL (overwrite on each run)."""
    s3 = boto3.client("s3", region_name=REGION)
    lines = [json.dumps(d) for d in dividends]
    s3.put_object(
        Bucket=BUCKET,
        Key="dividends/data.jsonl",
        Body="\n".join(lines),
        ContentType="application/x-ndjson",
    )
    print(f"Saved {len(dividends)} dividends to s3://{BUCKET}/dividends/data.jsonl")
