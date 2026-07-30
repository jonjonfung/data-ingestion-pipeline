from .api_client import get


def fetch_orders() -> list[dict]:
    """Fetch full order history with cursor-based pagination."""
    orders = []
    path = "/api/v0/equity/history/orders?limit=50"
    while path:
        data = get(path)
        for item in data.get("items", []):
            order = item.get("order", {})
            fill = item.get("fill", {})
            wallet = fill.get("walletImpact", {})
            taxes = wallet.get("taxes", [])
            fee = round(abs(sum(t.get("quantity", 0) for t in taxes)), 4)
            raw_ticker = order.get("ticker", "")
            orders.append({
                "order_id": order.get("id"),
                "ticker": raw_ticker.split("_")[0],
                "name": order.get("instrument", {}).get("name"),
                "side": order.get("side"),          # BUY or SELL
                "quantity": fill.get("quantity"),
                "price": fill.get("price"),
                "net_value_gbp": wallet.get("netValue"),
                "realised_pnl_gbp": wallet.get("realisedProfitLoss"),
                "fee_gbp": fee,
                "filled_at": (fill.get("filledAt") or "")[:10],
            })
        path = data.get("nextPagePath")
    return orders
