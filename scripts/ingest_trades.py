from etoro.trades import fetch_trades, save_trades

trades = fetch_trades(min_date="2020-01-01")
save_trades(trades)
print(f"Trades saved: {len(trades)}")
