from etoro.data_sources import fetch_portfolio
from etoro.data_loader import save_portfolio
from etoro.instruments import fetch_instruments, save_instruments


def main(event, context):
    # Fetch portfolio
    data = fetch_portfolio("real")
    save_portfolio(data)

    # Fetch and save instrument metadata for all positions
    instrument_ids = list({p["instrument_id"] for p in data["positions"] if p.get("instrument_id")})
    if instrument_ids:
        instruments = fetch_instruments(instrument_ids)
        save_instruments(instruments)

    print(f"Ingested {len(data['positions'])} positions | "
          f"Invested: ${data['total_invested']:,.2f} | "
          f"P&L: ${data['total_unrealized_pnl']:,.2f} | "
          f"Instruments: {len(instrument_ids)}")

    return {"status": "ok", "positions": len(data["positions"]), "instruments": len(instrument_ids)}
