"""
eToro CLI — fetch and display portfolio data.

Usage:
  python -m etoro.cli                  # real account, print only
  python -m etoro.cli --save           # real account, save to S3
  python -m etoro.cli --account demo   # demo account
"""

import argparse
from dotenv import load_dotenv

load_dotenv()

from .data_sources import fetch_portfolio
from .data_loader import save_portfolio


def print_portfolio(data: dict):
    print(f"\n=== eToro Portfolio ({data['account_type'].upper()}) ===")
    print(f"Total Invested:   ${data['total_invested']:,.2f}")
    print(f"Unrealized P&L:   ${data['total_unrealized_pnl']:,.2f}")
    print(f"\nOpen Positions ({len(data['positions'])}):")
    print(f"{'Instrument':<20} {'Invested':>12} {'P&L':>12}")
    print("-" * 46)
    for p in data["positions"]:
        print(f"{str(p['instrument_id']):<20} ${p['amount']:>10,.2f} ${p['unrealized_pnl']:>10,.2f}")


def main():
    parser = argparse.ArgumentParser(description="eToro data ingestion CLI")
    parser.add_argument("--account", choices=["real", "demo"], default="real")
    parser.add_argument("--save", action="store_true", help="Save snapshot to S3")
    args = parser.parse_args()

    data = fetch_portfolio(args.account)
    print_portfolio(data)

    if args.save:
        save_portfolio(data)


if __name__ == "__main__":
    main()
