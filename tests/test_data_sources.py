from unittest.mock import patch
from etoro.data_sources import fetch_portfolio

MOCK_PNL = {
    "positions": [
        {"instrumentId": 1001, "amount": 500.0, "unrealizedPnL": {"pnL": 42.5}},
        {"instrumentId": 1002, "amount": 250.0, "unrealizedPnL": {"pnL": -10.0}},
    ],
    "mirrors": [
        {
            "mirrorId": "m1",
            "positions": [
                {"instrumentId": 2001, "amount": 300.0, "unrealizedPnL": {"pnL": 15.0}},
            ],
        }
    ],
}


@patch("etoro.data_sources.get", return_value=MOCK_PNL)
def test_fetch_portfolio_positions(mock_get):
    result = fetch_portfolio("real")
    assert len(result["positions"]) == 3


@patch("etoro.data_sources.get", return_value=MOCK_PNL)
def test_fetch_portfolio_totals(mock_get):
    result = fetch_portfolio("real")
    assert result["total_invested"] == 1050.0
    assert result["total_unrealized_pnl"] == 47.5


@patch("etoro.data_sources.get", return_value=MOCK_PNL)
def test_fetch_portfolio_mirror_has_mirror_id(mock_get):
    result = fetch_portfolio("real")
    mirror_positions = [p for p in result["positions"] if "mirror_id" in p]
    assert len(mirror_positions) == 1
    assert mirror_positions[0]["mirror_id"] == "m1"


@patch("etoro.data_sources.get", return_value={"positions": [], "mirrors": []})
def test_fetch_portfolio_empty(mock_get):
    result = fetch_portfolio("real")
    assert result["total_invested"] == 0.0
    assert result["total_unrealized_pnl"] == 0.0
    assert result["positions"] == []
