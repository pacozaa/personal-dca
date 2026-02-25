"""CLI entry point — Analyze the best day of the month (1-7) to DCA buy stocks and crypto.

Environment variables:
    DCA_STOCKS: Comma-separated list of stock symbols (e.g. "AAPL,MSFT,GOOGL")
    DCA_CRYPTO: Comma-separated list of crypto symbols (e.g. "BTC,ETH")
    ALPHAVANTAGE_API_KEY: Your Alpha Vantage API key
"""

from __future__ import annotations

import time

from dca_stock.analysis import find_best_day
from dca_stock.api import fetch_daily_crypto_prices, fetch_daily_prices
from dca_stock.chart import save_chart, save_summary_chart
from dca_stock.config import DEFAULT_CRYPTO_MARKET, get_config
from dca_stock.display import print_analysis


def _process_symbol(
    symbol: str,
    time_series: dict[str, dict],
    overall_best: dict[str, int],
    all_results: dict[str, dict[int, dict]],
) -> None:
    """Run analysis, display results, and save chart for a single symbol."""
    results = find_best_day(time_series)
    print_analysis(symbol, results)

    if results:
        best_day = min(results, key=lambda d: results[d]["avg_normalized_price"])
        overall_best[symbol] = best_day
        all_results[symbol] = results

        chart_path = save_chart(symbol, results)
        if chart_path:
            print(f"  📊 Chart saved → {chart_path}")


def main() -> None:
    stock_symbols, crypto_symbols, api_key = get_config()

    all_symbols = stock_symbols + [f"{s} (crypto)" for s in crypto_symbols]
    print("DCA Best Buy Day Analysis")
    print(f"Analyzing: {', '.join(all_symbols)}")
    print("Target days: 1st through last day of each month")

    overall_best: dict[str, int] = {}
    all_results: dict[str, dict[int, dict]] = {}
    request_count = 0

    # --- Stocks ---
    for symbol in stock_symbols:
        if request_count > 0:
            time.sleep(2)  # Respect free-tier rate limit
        request_count += 1

        print(f"\nFetching stock data for {symbol}...", end=" ", flush=True)
        time_series = fetch_daily_prices(symbol, api_key)

        if not time_series:
            print("skipped.")
            continue

        print(f"got {len(time_series)} trading days.")
        _process_symbol(symbol, time_series, overall_best, all_results)

    # --- Crypto ---
    for symbol in crypto_symbols:
        if request_count > 0:
            time.sleep(2)
        request_count += 1

        print(f"\nFetching crypto data for {symbol}...", end=" ", flush=True)
        time_series = fetch_daily_crypto_prices(symbol, api_key, market=DEFAULT_CRYPTO_MARKET)

        if not time_series:
            print("skipped.")
            continue

        print(f"got {len(time_series)} days.")
        _process_symbol(symbol, time_series, overall_best, all_results)

    # --- Summary ---
    if overall_best:
        print(f"\n{'=' * 60}")
        print("  SUMMARY — Best Day to Buy Each Asset")
        print(f"{'=' * 60}")
        for sym, day in sorted(overall_best.items(), key=lambda x: x[1]):
            print(f"  {sym:<10} → Day {day}")
        print()

        summary_path = save_summary_chart(overall_best, all_results)
        if summary_path:
            print(f"  📊 Summary chart saved → {summary_path}")


if __name__ == "__main__":
    main()
