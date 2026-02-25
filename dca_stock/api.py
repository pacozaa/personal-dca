"""Alpha Vantage API client for fetching stock price data."""

from __future__ import annotations

import requests

from dca_stock.config import ALPHA_VANTAGE_BASE_URL


def fetch_daily_prices(symbol: str, api_key: str) -> dict[str, dict]:
    """Fetch daily time series data from Alpha Vantage.

    Returns a dict mapping date strings (YYYY-MM-DD) to OHLCV dicts.
    Uses outputsize=full to get 20+ years of history (premium),
    falls back to compact (100 data points) on free tier.
    """
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": api_key,
    }

    resp = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # Check for API error messages
    if "Error Message" in data:
        print(f"  API error for {symbol}: {data['Error Message']}")
        return {}
    if "Note" in data:
        print(f"  API rate limit note: {data['Note']}")
        return {}
    if "Information" in data:
        print(f"  API info: {data['Information']}")
        return {}

    time_series = data.get("Time Series (Daily)", {})
    if not time_series:
        print(f"  No daily data returned for {symbol}.")
        return {}

    return time_series
