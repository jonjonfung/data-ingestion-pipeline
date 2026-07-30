import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()  # picks up .env in repo root when run locally

from sources.trading212.data_sources import fetch_portfolio
from sources.trading212.data_loader import save_portfolio, save_orders
from sources.trading212.dividends import fetch_dividends, save_dividends
from sources.trading212.orders import fetch_orders

data = fetch_portfolio()
save_portfolio(data)
print(
    f"Positions: {len(data['positions'])} | "
    f"Invested: £{data['total_invested']:,.2f} | "
    f"Value: £{data['total_value']:,.2f} | "
    f"P&L: £{data['total_ppl']:,.2f}"
)

dividends = fetch_dividends()
save_dividends(dividends)
print(f"Dividends: {len(dividends)} records saved")

orders = fetch_orders()
save_orders(orders)
print(f"Orders: {len(orders)} records saved")
