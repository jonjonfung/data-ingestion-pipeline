from etoro.data_sources import fetch_portfolio
from etoro.data_loader import save_portfolio
from etoro.instruments import fetch_instruments, save_instruments
from etoro.trades import fetch_trades, save_trades


def main(event, context):
    # Fetch portfolio
    data = fetch_portfolio("real")
    save_portfolio(data)

    # Fetch and save instrument metadata
    instrument_ids = list({p["instrument_id"] for p in data["positions"] if p.get("instrument_id")})
    if instrument_ids:
        instruments = fetch_instruments(instrument_ids)
        save_instruments(instruments)

    # Fetch and save full trade history
    trades = fetch_trades(min_date="2020-01-01")
    save_trades(trades)

    print(f"Ingested {len(data['positions'])} positions | "
          f"Invested: ${data['total_invested']:,.2f} | "
          f"P&L: ${data['total_unrealized_pnl']:,.2f} | "
          f"Instruments: {len(instrument_ids)} | "
          f"Trades: {len(trades)}")

    return {
        "status": "ok",
        "positions": len(data["positions"]),
        "instruments": len(instrument_ids),
        "trades": len(trades),
    }
