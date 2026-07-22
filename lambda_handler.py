from etoro.data_sources import fetch_portfolio
from etoro.data_loader import save_portfolio


def main(event, context):
    data = fetch_portfolio("real")
    save_portfolio(data)

    print(f"Ingested {len(data['positions'])} positions | "
          f"Invested: ${data['total_invested']:,.2f} | "
          f"P&L: ${data['total_unrealized_pnl']:,.2f}")

    return {"status": "ok", "positions": len(data["positions"])}
