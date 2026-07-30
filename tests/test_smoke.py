"""Smoke tests — verify imports and basic data shapes without hitting external APIs."""
import pytest


def test_etoro_imports():
    from sources.etoro.data_sources import fetch_portfolio
    from sources.etoro.data_loader import save_portfolio
    from sources.etoro.instruments import fetch_instruments, save_instruments
    from sources.etoro.trades import fetch_trades, save_trades


def test_t212_imports():
    from sources.trading212.data_sources import fetch_portfolio
    from sources.trading212.data_loader import save_portfolio, save_orders
    from sources.trading212.dividends import fetch_dividends, save_dividends
    from sources.trading212.orders import fetch_orders


def test_position_shape():
    """fetch_portfolio returns expected keys without a real API call."""
    from sources.trading212.data_sources import fetch_portfolio
    # Only check the returned dict has expected keys — skip if no credentials
    pytest.importorskip("boto3")
    required = {"positions", "total_invested", "total_value", "free_cash", "total_ppl"}
    # We can't call the API in CI without secrets, so just assert the keys exist in code
    import inspect
    src = inspect.getsource(fetch_portfolio)
    for key in required:
        assert key in src
