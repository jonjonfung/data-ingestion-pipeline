"""
Fetch portfolio positions, total invested, and unrealized P&L from eToro.
"""

from . import get


def get_summary(account_type: str = "real") -> dict:
    """
    Returns a clean summary of open positions with invested amounts and P&L.
    account_type: 'real' or 'demo'
    """
    data = get(f"/trading/info/{account_type}/pnl")

    positions = []

    for p in data.get("positions", []):
        positions.append({
            "instrument_id": p.get("instrumentId"),
            "amount": p.get("amount", 0),
            "unrealized_pnl": p.get("unrealizedPnL", {}).get("pnL", 0),
        })

    for mirror in data.get("mirrors", []):
        for p in mirror.get("positions", []):
            positions.append({
                "instrument_id": p.get("instrumentId"),
                "amount": p.get("amount", 0),
                "unrealized_pnl": p.get("unrealizedPnL", {}).get("pnL", 0),
                "mirror_id": mirror.get("mirrorId"),
            })

    total_invested = sum(p["amount"] for p in positions)
    total_pnl = sum(p["unrealized_pnl"] for p in positions)

    return {
        "account_type": account_type,
        "positions": positions,
        "total_invested": round(total_invested, 2),
        "total_unrealized_pnl": round(total_pnl, 2),
    }


def print_summary(account_type: str = "real"):
    summary = get_summary(account_type)

    print(f"\n=== eToro Portfolio ({summary['account_type'].upper()}) ===")
    print(f"Total Invested:   ${summary['total_invested']:,.2f}")
    print(f"Unrealized P&L:   ${summary['total_unrealized_pnl']:,.2f}")
    print(f"\nOpen Positions ({len(summary['positions'])}):")
    print(f"{'Instrument':<20} {'Invested':>12} {'P&L':>12}")
    print("-" * 46)
    for p in summary["positions"]:
        print(f"{str(p['instrument_id']):<20} ${p['amount']:>10,.2f} ${p['unrealized_pnl']:>10,.2f}")


if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv()
    account_type = sys.argv[1] if len(sys.argv) > 1 else "real"
    print_summary(account_type)
