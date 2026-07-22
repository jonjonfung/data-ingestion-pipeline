import json
import boto3
from .api_client import get

BUCKET = "etoro-pipeline-john"
REGION = "ap-southeast-2"


def fetch_trades(min_date: str = "2020-01-01") -> list[dict]:
    """
    Fetch all closed trade history from eToro (paginated).
    min_date: earliest trade date to fetch (YYYY-MM-DD)
    """
    trades = []
    page = 1

    while True:
        data = get(f"/trading/info/trade/history?minDate={min_date}&page={page}&pageSize=100")
        items = data.get("history", data.get("items", []))

        if not items:
            break

        for t in items:
            trades.append({
                "trade_id": t.get("positionId"),
                "instrument_id": t.get("instrumentId"),
                "is_buy": t.get("isBuy"),
                "open_date": t.get("openTimestamp", "")[:10],
                "close_date": t.get("closeTimestamp", "")[:10],
                "investment": t.get("investment", 0),
                "net_profit": t.get("netProfit", 0),
                "open_rate": t.get("openRate"),
                "close_rate": t.get("closeRate"),
                "fees": t.get("fees", 0),
                "leverage": t.get("leverage", 1),
            })

        if len(items) < 100:
            break
        page += 1

    return trades


def save_trades(trades: list[dict]):
    """
    Save all trades to S3 as JSONL (overwrite on each run).
    s3://etoro-pipeline-john/trades/data.jsonl
    """
    s3 = boto3.client("s3", region_name=REGION)
    lines = [json.dumps(t) for t in trades]
    s3.put_object(
        Bucket=BUCKET,
        Key="trades/data.jsonl",
        Body="\n".join(lines),
        ContentType="application/x-ndjson",
    )
    print(f"Saved {len(trades)} trades to s3://{BUCKET}/trades/data.jsonl")
