"""Configuration loading from environment variables."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Walk up from this file to find .env at the repo root
_repo_root = Path(__file__).resolve().parents[1]
load_dotenv(_repo_root / ".env")

ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
TARGET_DAYS = range(1, 8)  # Days 1 through 7
DEFAULT_CRYPTO_MARKET = "USD"  # Fiat currency for crypto price conversion


def get_config() -> tuple[list[str], list[str], str]:
    """Read stock/crypto symbols and API key from environment variables.

    Returns:
        A tuple of (stock_symbols, crypto_symbols, api_key).
    """
    raw_stocks = os.environ.get("DCA_STOCKS", "")
    raw_crypto = os.environ.get("DCA_CRYPTO", "")

    if not raw_stocks and not raw_crypto:
        print("Error: Neither DCA_STOCKS nor DCA_CRYPTO environment variable is set.")
        print(
            "Usage: DCA_STOCKS='AAPL,MSFT' DCA_CRYPTO='BTC,ETH' "
            "ALPHAVANTAGE_API_KEY='your_key' dca-stock-analyze"
        )
        sys.exit(1)

    stock_symbols = [s.strip().upper() for s in raw_stocks.split(",") if s.strip()]
    crypto_symbols = [s.strip().upper() for s in raw_crypto.split(",") if s.strip()]

    if not stock_symbols and not crypto_symbols:
        print("Error: DCA_STOCKS and DCA_CRYPTO contain no valid symbols.")
        sys.exit(1)

    api_key = os.environ.get("ALPHAVANTAGE_API_KEY", "")
    if not api_key:
        print("Error: ALPHAVANTAGE_API_KEY environment variable is not set.")
        print("Get a free key at https://www.alphavantage.co/support/#api-key")
        sys.exit(1)

    return stock_symbols, crypto_symbols, api_key
