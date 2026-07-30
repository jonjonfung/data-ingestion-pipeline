from sources.etoro.data_sources import fetch_portfolio
from sources.etoro.data_loader import save_portfolio
from sources.etoro.instruments import fetch_instruments, save_instruments
from sources.etoro.trades import fetch_trades, save_trades
from sources.trading212.data_sources import fetch_portfolio as t212_fetch_portfolio
from sources.trading212.data_loader import save_portfolio as t212_save_portfolio
from sources.trading212.dividends import fetch_dividends, save_dividends
from sources.trading212.orders import fetch_orders
from sources.trading212.data_loader import save_orders as t212_save_orders


def main(event, context):
    # --- eToro ---
    data = fetch_portfolio("real")
    save_portfolio(data)

    instrument_ids = list({p["instrument_id"] for p in data["positions"] if p.get("instrument_id")})
    if instrument_ids:
        instruments = fetch_instruments(instrument_ids)
        save_instruments(instruments)

    trades = fetch_trades(min_date="2020-01-01")
    save_trades(trades)

    print(f"eToro: {len(data['positions'])} positions | "
          f"Invested: ${data['total_invested']:,.2f} | "
          f"P&L: ${data['total_unrealized_pnl']:,.2f} | "
          f"Instruments: {len(instrument_ids)} | "
          f"Trades: {len(trades)}")

    # --- Trading212 ---
    t212_data = t212_fetch_portfolio()
    t212_save_portfolio(t212_data)

    dividends = fetch_dividends()
    save_dividends(dividends)

    orders = fetch_orders()
    t212_save_orders(orders)

    print(f"Trading212: {len(t212_data['positions'])} positions | "
          f"Invested: £{t212_data['total_invested']:,.2f} | "
          f"Value: £{t212_data['total_value']:,.2f} | "
          f"P&L: £{t212_data['total_ppl']:,.2f} | "
          f"Dividends: {len(dividends)} | "
          f"Orders: {len(orders)}")

    return {
        "status": "ok",
        "etoro_positions": len(data["positions"]),
        "etoro_instruments": len(instrument_ids),
        "etoro_trades": len(trades),
        "t212_positions": len(t212_data["positions"]),
        "t212_dividends": len(dividends),
        "t212_orders": len(orders),
    }
