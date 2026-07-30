import json
import boto3
from .api_client import get

BUCKET = "etoro-pipeline-john"
REGION = "ap-southeast-2"


def fetch_instruments(instrument_ids: list[int]) -> list[dict]:
    """
    Fetch instrument metadata (name, symbol, type) for a list of IDs.
    """
    ids_param = ",".join(str(i) for i in instrument_ids if i)
    data = get(f"/market-data/instruments?ids={ids_param}")

    instruments = []
    for item in data.get("instrumentDisplayDatas", []):
        instruments.append({
            "instrument_id": item.get("instrumentID"),
            "name": item.get("instrumentDisplayName"),
            "symbol": item.get("internalSymbolFull"),
            "type_id": item.get("instrumentTypeID"),
        })
    return instruments


def save_instruments(instruments: list[dict]):
    """
    Save instrument metadata to S3 as JSONL.
    s3://etoro-pipeline-john/instruments/data.jsonl
    (Not partitioned — this is a slowly-changing reference table)
    """
    s3 = boto3.client("s3", region_name=REGION)
    lines = [json.dumps(i) for i in instruments]
    s3.put_object(
        Bucket=BUCKET,
        Key="instruments/data.jsonl",
        Body="\n".join(lines),
        ContentType="application/x-ndjson",
    )
    print(f"Saved {len(instruments)} instruments to s3://{BUCKET}/instruments/data.jsonl")
