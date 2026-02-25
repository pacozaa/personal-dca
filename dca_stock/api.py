"""Alpha Vantage API client for fetching stock and crypto price data."""

from __future__ import annotations

import requests

from dca_stock.config import ALPHA_VANTAGE_BASE_URL


def _check_api_errors(data: dict, symbol: str) -> bool:
    """Check for common Alpha Vantage API errors. Returns True if an error was found."""
    if "Error Message" in data:
        print(f"  API error for {symbol}: {data['Error Message']}")
        return True
    if "Note" in data:
        print(f"  API rate limit note: {data['Note']}")
        return True
    if "Information" in data:
        print(f"  API info: {data['Information']}")
        return True
    return False


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

    if _check_api_errors(data, symbol):
        return {}

    time_series = data.get("Time Series (Daily)", {})
    if not time_series:
        print(f"  No daily data returned for {symbol}.")
        return {}

    return time_series


def _normalize_crypto_entry(entry: dict, market: str) -> dict:
    """Normalize a crypto OHLCV entry to match the stock format ("4. close" key).

    Alpha Vantage crypto responses may use either:
      - Simple keys: "1. open", "4. close", etc.
      - Market-specific keys: "1a. open (USD)", "4a. close (USD)", etc.
    """
    # If standard stock-style keys already exist, return as-is
    if "4. close" in entry:
        return entry

    market_upper = market.upper()
    normalized: dict[str, str] = {}
    # Map from market-specific keys to standard keys
    key_map = {
        f"1a. open ({market_upper})": "1. open",
        f"2a. high ({market_upper})": "2. high",
        f"3a. low ({market_upper})": "3. low",
        f"4a. close ({market_upper})": "4. close",
        f"5. volume": "5. volume",
        f"6. market cap ({market_upper})": "6. market cap",
    }
    for src_key, dst_key in key_map.items():
        if src_key in entry:
            normalized[dst_key] = entry[src_key]

    # Fallback: try to find any key containing "close"
    if "4. close" not in normalized:
        for key, val in entry.items():
            if "close" in key.lower():
                normalized["4. close"] = val
                break

    return normalized if normalized else entry


def fetch_daily_crypto_prices(symbol: str, api_key: str, market: str = "USD") -> dict[str, dict]:
    """Fetch daily crypto prices from Alpha Vantage.

    Uses the DIGITAL_CURRENCY_DAILY endpoint.
    Returns a dict mapping date strings (YYYY-MM-DD) to OHLCV dicts
    normalized to use the same keys as stock data ("4. close", etc.).
    """
    params = {
        "function": "DIGITAL_CURRENCY_DAILY",
        "symbol": symbol,
        "market": market,
        "apikey": api_key,
    }

    resp = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if _check_api_errors(data, symbol):
        return {}

    time_series = data.get("Time Series (Digital Currency Daily)", {})
    if not time_series:
        print(f"  No daily crypto data returned for {symbol}.")
        return {}

    # Normalize keys so downstream analysis can use "4. close" uniformly
    return {date_str: _normalize_crypto_entry(entry, market) for date_str, entry in time_series.items()}
