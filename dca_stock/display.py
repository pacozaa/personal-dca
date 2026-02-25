"""Display and formatting utilities for analysis results."""

from __future__ import annotations

from dca_stock.config import TARGET_DAYS


def print_analysis(symbol: str, results: dict[int, dict]) -> None:
    """Pretty-print the analysis results for a single stock."""
    if not results:
        print(f"\n{'=' * 60}")
        print(f"  {symbol}: Insufficient data for analysis")
        print(f"{'=' * 60}")
        return

    # Find the best day (lowest normalized price)
    best_day = min(results, key=lambda d: results[d]["avg_normalized_price"])

    print(f"\n{'=' * 60}")
    print(f"  {symbol} — Best Day of Month to Buy (Days 1-31)")
    print(f"{'=' * 60}")
    print(f"  {'Day':<6} {'Norm. Price':<14} {'Avg Close ($)':<16} {'Months':<8}")
    print(f"  {'-' * 50}")

    for day in TARGET_DAYS:
        if day not in results:
            continue
        r = results[day]
        marker = " ◀ BEST" if day == best_day else ""
        print(
            f"  {day:<6} {r['avg_normalized_price']:<14.6f} "
            f"{r['avg_raw_price']:<16.2f} {r['sample_count']:<8}{marker}"
        )

    print(f"\n  ➜ Best day to buy {symbol}: Day {best_day} of the month")
    savings_pct = (1 - results[best_day]["avg_normalized_price"]) * 100
    if savings_pct > 0:
        print(f"    (historically {savings_pct:.3f}% below monthly average)")
    else:
        print(f"    (historically {abs(savings_pct):.3f}% above monthly average)")
    print()
