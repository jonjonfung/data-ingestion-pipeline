"""
Backfill weekly portfolio snapshots into S3 using yfinance historical prices.

For each current open position, fetches 2 years of weekly prices and writes
synthetic historical snapshots so the Portfolio vs S&P 500 chart has data.

Usage:
    PYTHONPATH=. python scripts/backfill_history.py
"""

import json
import os
import boto3
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

BUCKET = "etoro-pipeline-john"
REGION = os.getenv("AWS_DEFAULT_REGION", "ap-southeast-2")

# Manual ticker mapping — eToro API returns null for internalSymbolFull
TICKER_MAP = {
    1003:  ("META",  "Meta Platforms Inc"),
    1023:  ("JPM",   "JPMorgan Chase & Co"),
    1130:  ("MU",    "Micron Technology"),
    1141:  ("BIDU",  "Baidu ADR"),
    1155:  ("BABA",  "Alibaba ADR"),
    1583:  ("MO",    "Altria Group"),
    1634:  ("TXN",   "Texas Instruments"),
    1757:  ("NEM",   "Newmont Mining"),
    3008:  ("XLE",   "Energy Select Sector SPDR"),
    3190:  ("GLDM",  "SPDR Gold MiniShares"),
    3251:  ("VHT",   "Vanguard Health Care ETF"),
    4236:  ("AVGO",  "Broadcom Inc"),
    4238:  ("VOO",   "Vanguard S&P 500 ETF"),
    4244:  ("ASML",  "ASML Holding"),
    4260:  ("NOW",   "ServiceNow Inc"),
    4430:  ("SLV",   "iShares Silver Trust"),
    4481:  ("TSM",   "Taiwan Semiconductor ADR"),
    4498:  ("BNDX",  "Vanguard Total International Bond ETF"),
    6368:  ("VXUS",  "Vanguard Total International Stock ETF"),
    6434:  ("GOOGL", "Alphabet Inc Class A"),
    8748:  ("URA",   "Global X Uranium ETF"),
    9425:  ("IONQ",  "IONQ Inc"),
}


def load_current_positions() -> list[dict]:
    s3 = boto3.client("s3", region_name=REGION)
    # Find the most recent positions date
    resp = s3.list_objects_v2(Bucket=BUCKET, Prefix="positions/", Delimiter="/")
    prefixes = [p["Prefix"] for p in resp.get("CommonPrefixes", [])]
    latest = sorted(prefixes)[-1]  # e.g. positions/date=2026-07-23/

    obj = s3.get_object(Bucket=BUCKET, Key=f"{latest}data.jsonl")
    lines = obj["Body"].read().decode().strip().split("\n")
    return [json.loads(l) for l in lines if l]


def get_weekly_mondays(years: int = 2) -> list[str]:
    end = pd.Timestamp.today().normalize()
    start = end - pd.DateOffset(years=years)
    mondays = pd.date_range(start=start, end=end, freq="W-MON")
    return [d.strftime("%Y-%m-%d") for d in mondays]


def fetch_ticker_prices(ticker: str, start: str, end: str) -> pd.Series:
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if df.empty:
        return pd.Series(dtype=float)
    return df["Close"].squeeze()


def main():
    s3 = boto3.client("s3", region_name=REGION)
    positions = load_current_positions()
    print(f"Loaded {len(positions)} current positions")

    dates = get_weekly_mondays(years=2)
    start_date = dates[0]
    end_date = (pd.Timestamp.today() + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    # Fetch current prices and history for each ticker
    price_history = {}  # instrument_id → pd.Series indexed by date string
    for pos in positions:
        iid = pos["instrument_id"]
        if iid not in TICKER_MAP:
            print(f"  Skipping instrument_id {iid} — no ticker mapping")
            continue

        ticker, name = TICKER_MAP[iid]
        print(f"  Fetching {ticker} ({name})...")
        prices = fetch_ticker_prices(ticker, start_date, end_date)
        if prices.empty:
            print(f"    No data for {ticker}")
            continue

        prices.index = pd.to_datetime(prices.index).tz_localize(None)
        price_history[iid] = prices

    # For each Monday, write a position snapshot
    existing_keys = set()
    resp = s3.list_objects_v2(Bucket=BUCKET, Prefix="positions/")
    for obj in resp.get("Contents", []):
        existing_keys.add(obj["Key"])

    written = 0
    for date_str in dates:
        key = f"positions/date={date_str}/data.jsonl"

        # Skip dates that already have real snapshots
        if key in existing_keys:
            print(f"  Skipping {date_str} — snapshot already exists")
            continue

        target_date = pd.Timestamp(date_str)
        lines = []

        for pos in positions:
            iid = pos["instrument_id"]
            if iid not in price_history:
                continue

            prices = price_history[iid]
            # Get closest price on or before this date
            past = prices[prices.index <= target_date]
            if past.empty:
                continue
            hist_price = float(past.iloc[-1])

            # Get current price (last available)
            curr_price = float(prices.iloc[-1])
            if curr_price == 0:
                continue

            # Scale position value by price ratio
            current_value = pos["amount"] + pos["unrealized_pnl"]
            hist_value = current_value * (hist_price / curr_price)
            hist_pnl = round(hist_value - pos["amount"], 2)

            lines.append(json.dumps({
                "instrument_id": iid,
                "amount": pos["amount"],
                "unrealized_pnl": hist_pnl,
                "mirror_id": pos.get("mirror_id"),
                "date": date_str,
            }))

        if lines:
            s3.put_object(
                Bucket=BUCKET,
                Key=key,
                Body="\n".join(lines),
                ContentType="application/x-ndjson",
            )
            print(f"  Wrote {len(lines)} positions for {date_str}")
            written += 1

    print(f"\nDone — wrote {written} historical snapshots")
    print("Run MSCK REPAIR TABLE etoro_db.positions in Athena to register partitions")


if __name__ == "__main__":
    main()
