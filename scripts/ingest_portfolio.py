from etoro.data_sources import fetch_portfolio
from etoro.data_loader import save_portfolio
from etoro.instruments import fetch_instruments, save_instruments

data = fetch_portfolio("real")
save_portfolio(data)
print(f"Positions: {len(data['positions'])} | Invested: ${data['total_invested']:,.2f} | P&L: ${data['total_unrealized_pnl']:,.2f}")

ids = list({p["instrument_id"] for p in data["positions"] if p.get("instrument_id")})
if ids:
    instruments = fetch_instruments(ids)
    save_instruments(instruments)
    print(f"Instruments saved: {len(instruments)}")
