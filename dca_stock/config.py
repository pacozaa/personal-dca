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


def get_config() -> tuple[list[str], str]:
    """Read stock symbols and API key from environment variables."""
    raw_stocks = os.environ.get("DCA_STOCKS", "")
    if not raw_stocks:
        print("Error: DCA_STOCKS environment variable is not set.")
        print("Usage: DCA_STOCKS='AAPL,MSFT' ALPHAVANTAGE_API_KEY='your_key' dca-stock-analyze")
        sys.exit(1)

    symbols = [s.strip().upper() for s in raw_stocks.split(",") if s.strip()]
    if not symbols:
        print("Error: DCA_STOCKS contains no valid symbols.")
        sys.exit(1)

    api_key = os.environ.get("ALPHAVANTAGE_API_KEY", "")
    if not api_key:
        print("Error: ALPHAVANTAGE_API_KEY environment variable is not set.")
        print("Get a free key at https://www.alphavantage.co/support/#api-key")
        sys.exit(1)

    return symbols, api_key
