from .api_client import get


def fetch_portfolio() -> dict:
    """
    Fetch portfolio positions and account summary from Trading212.
    Returns positions with P&L and account-level cash metrics.
    """
    summary = get("/api/v0/equity/account/summary")
    raw_positions = get("/api/v0/equity/positions")

    positions = []
    for p in raw_positions:
        instrument = p.get("instrument", {})
        wallet = p.get("walletImpact", {})
        raw_ticker = instrument.get("ticker", "")
        positions.append({
            "ticker": raw_ticker.split("_")[0],
            "name": instrument.get("name"),
            "quantity": p.get("quantity", 0),
            "avg_price": p.get("averagePricePaid", 0),
            "current_price": p.get("currentPrice", 0),
            "value": wallet.get("currentValue", 0),
            "ppl": wallet.get("unrealizedProfitLoss", 0),
            "fx_ppl": wallet.get("fxImpact", 0),
            "initial_fill_date": p.get("createdAt", "")[:10],
        })

    investments = summary.get("investments", {})
    total_ppl = round(sum(p["ppl"] for p in positions), 2)

    return {
        "positions": positions,
        "total_invested": round(investments.get("totalCost", 0), 2),
        "total_value": round(summary.get("totalValue", 0), 2),
        "free_cash": round(summary.get("cash", {}).get("availableToTrade", 0), 2),
        "total_ppl": total_ppl,
    }
