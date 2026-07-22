from .api_client import get


def fetch_portfolio(account_type: str = "real") -> dict:
    """
    Fetch raw portfolio positions, invested amounts, and P&L from eToro.
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
