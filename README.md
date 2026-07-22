# data-ingestion-pipeline

Data ingestion pipelines for pulling personal finance and trading data from external platforms.

## Structure

```
etoro/
  __init__.py     # Base HTTP client (auth headers, base URL)
  portfolio.py    # Portfolio positions, invested amounts, P&L
```

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your keys:
   ```
   ETORO_PUBLIC_KEY=your_public_key
   ETORO_PRIVATE_KEY=your_private_key
   ```
   Get your keys from eToro: Settings > Trading > API Key Management

3. Run the portfolio pipeline:
   ```bash
   python -m etoro.portfolio
   # or for demo account:
   python -m etoro.portfolio demo
   ```

## Adding a new source

Create a new top-level folder (e.g. `robinhood/`, `coinbase/`) with its own `__init__.py` for auth and individual files per data domain.
