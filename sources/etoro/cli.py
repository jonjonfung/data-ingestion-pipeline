"""
eToro CLI — full data ingestion (portfolio, instruments, trades).

Usage:
  python -m etoro.cli                  # print only
  python -m etoro.cli --save           # fetch and save all data to S3
  python -m etoro.cli --account demo   # demo account
"""

import argparse
from dotenv import load_dotenv
from .data_sources import fetch_portfolio
from .data_loader import save_portfolio
from .instruments import fetch_instruments, save_instruments
from .trades import fetch_trades, save_trades

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="eToro data ingestion CLI")
    parser.add_argument("--account", choices=["real", "demo"], default="real")
    parser.add_argument("--save", action="store_true", help="Save all data to S3")
    args = parser.parse_args()

    # Portfolio + positions
    data = fetch_portfolio(args.account)
    print(f"\n=== eToro Portfolio ({data['account_type'].upper()}) ===")
    print(f"Total Invested:   ${data['total_invested']:,.2f}")
    print(f"Unrealized P&L:   ${data['total_unrealized_pnl']:,.2f}")
    print(f"Open Positions:   {len(data['positions'])}")

    if args.save:
        save_portfolio(data)

    # Instruments
    instrument_ids = list({p["instrument_id"] for p in data["positions"] if p.get("instrument_id")})
    if instrument_ids:
        instruments = fetch_instruments(instrument_ids)
        print(f"Instruments:      {len(instruments)}")
        if args.save:
            save_instruments(instruments)

    # Trades
    trades = fetch_trades(min_date="2020-01-01")
    print(f"Closed Trades:    {len(trades)}")
    if args.save:
        save_trades(trades)


if __name__ == "__main__":
    main()
