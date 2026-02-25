"""CLI entry point — Analyze the best day of the month (1-7) to DCA buy stocks.

Environment variables:
    DCA_STOCKS: Comma-separated list of stock symbols (e.g. "AAPL,MSFT,GOOGL")
    ALPHAVANTAGE_API_KEY: Your Alpha Vantage API key
"""

from __future__ import annotations

import time

from dca_stock.analysis import find_best_day
from dca_stock.api import fetch_daily_prices
from dca_stock.config import get_config
from dca_stock.display import print_analysis


def main() -> None:
    symbols, api_key = get_config()

    print("DCA Best Buy Day Analysis")
    print(f"Analyzing stocks: {', '.join(symbols)}")
    print("Target days: 1st through 7th of each month")

    overall_best: dict[str, int] = {}

    for i, symbol in enumerate(symbols):
        if i > 0:
            time.sleep(2)  # Respect free-tier rate limit
        print(f"\nFetching data for {symbol}...", end=" ", flush=True)
        time_series = fetch_daily_prices(symbol, api_key)

        if not time_series:
            print("skipped.")
            continue

        print(f"got {len(time_series)} trading days.")
        results = find_best_day(time_series)
        print_analysis(symbol, results)

        if results:
            best_day = min(results, key=lambda d: results[d]["avg_normalized_price"])
            overall_best[symbol] = best_day

    # Summary
    if overall_best:
        print(f"\n{'=' * 60}")
        print("  SUMMARY — Best Day to Buy Each Stock")
        print(f"{'=' * 60}")
        for sym, day in overall_best.items():
            print(f"  {sym:<10} → Day {day}")
        print()


if __name__ == "__main__":
    main()
