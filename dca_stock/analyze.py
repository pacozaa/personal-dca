"""CLI entry point — Analyze the best day of the month (1-7) to DCA buy stocks and crypto.

Environment variables:
    DCA_STOCKS: Comma-separated list of stock symbols (e.g. "AAPL,MSFT,GOOGL")
    DCA_CRYPTO: Comma-separated list of crypto symbols (e.g. "BTC,ETH")
    ALPHAVANTAGE_API_KEY: Your Alpha Vantage API key
"""

from __future__ import annotations

import argparse
import time

from dca_stock.analysis import find_best_day, find_best_month, find_best_weekday
from dca_stock.api import fetch_daily_crypto_prices, fetch_daily_prices
from dca_stock.chart import save_chart, save_month_chart, save_summary_chart, save_weekday_chart
from dca_stock.config import DEFAULT_CRYPTO_MARKET, get_config
from dca_stock.display import (
    print_analysis,
    print_analysis_markdown,
    print_month_analysis,
    print_month_analysis_markdown,
    print_weekday_analysis,
    print_weekday_analysis_markdown,
)


def _process_symbol(
    symbol: str,
    time_series: dict[str, dict],
    overall_best: dict[str, int],
    all_results: dict[str, dict[int, dict]],
    output_format: str = "text",
) -> None:
    """Run all analyses (day-of-month, weekday, seasonality), display results, and save charts."""
    # --- Best day of month ---
    results = find_best_day(time_series)
    if output_format == "markdown":
        print_analysis_markdown(symbol, results)
    else:
        print_analysis(symbol, results)

    if results:
        best_day = min(results, key=lambda d: results[d]["avg_normalized_price"])
        overall_best[symbol] = best_day
        all_results[symbol] = results

        chart_path = save_chart(symbol, results)
        if chart_path:
            print(f"  📊 Chart saved → {chart_path}")

    # --- Best weekday ---
    wd_results = find_best_weekday(time_series)
    if output_format == "markdown":
        print_weekday_analysis_markdown(symbol, wd_results)
    else:
        print_weekday_analysis(symbol, wd_results)

    if wd_results:
        wd_chart_path = save_weekday_chart(symbol, wd_results)
        if wd_chart_path:
            print(f"  📊 Weekday chart saved → {wd_chart_path}")

    # --- Best month of year (seasonality) ---
    month_results = find_best_month(time_series)
    if output_format == "markdown":
        print_month_analysis_markdown(symbol, month_results)
    else:
        print_month_analysis(symbol, month_results)

    if month_results:
        month_chart_path = save_month_chart(symbol, month_results)
        if month_chart_path:
            print(f"  📊 Seasonality chart saved → {month_chart_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="DCA Best Buy Day Analysis")
    parser.add_argument(
        "--output-format",
        choices=["text", "markdown"],
        default="text",
        help="Output format: 'text' (default) for plain text, 'markdown' for GitHub-flavoured Markdown",
    )
    args = parser.parse_args()
    output_format: str = args.output_format

    stock_symbols, crypto_symbols, api_key = get_config()

    all_symbols = stock_symbols + [f"{s} (crypto)" for s in crypto_symbols]
    if output_format == "markdown":
        print("## 📊 DCA Best Buy Day Analysis\n")
        print(f"**Analyzing:** {', '.join(all_symbols)}\n")
    else:
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
        _process_symbol(symbol, time_series, overall_best, all_results, output_format)

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
        _process_symbol(symbol, time_series, overall_best, all_results, output_format)

    # --- Summary ---
    if overall_best:
        if output_format == "markdown":
            print("\n## 🏆 Summary — Best Day to Buy Each Asset\n")
            print("| Asset | Best Day |")
            print("|-------|----------|")
            for sym, day in sorted(overall_best.items(), key=lambda x: x[1]):
                print(f"| {sym} | Day {day} |")
            print()
        else:
            print(f"\n{'=' * 60}")
            print("  SUMMARY — Best Day to Buy Each Asset")
            print(f"{'=' * 60}")
            for sym, day in sorted(overall_best.items(), key=lambda x: x[1]):
                print(f"  {sym:<10} → Day {day}")
            print()

        summary_path = save_summary_chart(overall_best, all_results)
        if summary_path:
            print(f"  📊 Summary chart saved → {summary_path}")

    # --- API Request Usage ---
    if output_format == "markdown":
        print(f"\n> 📡 **API requests used this run:** {request_count}\n")
    else:
        print(f"\n📡 API requests used this run: {request_count}")


if __name__ == "__main__":
    main()

