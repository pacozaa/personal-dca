"""Display and formatting utilities for analysis results."""

from __future__ import annotations

from dca_stock.config import MONTH_NAMES, TARGET_DAYS, WEEKDAY_NAMES


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
    print(f"  {'Day':<6} {'Norm. Price':<14} {'Std Dev':<10} {'Avg Close ($)':<16} {'Months':<8}")
    print(f"  {'-' * 56}")

    for day in TARGET_DAYS:
        if day not in results:
            continue
        r = results[day]
        marker = " ◀ BEST" if day == best_day else ""
        print(
            f"  {day:<6} {r['avg_normalized_price']:<14.6f} {r['std_normalized_price']:<10.6f}"
            f" {r['avg_raw_price']:<16.2f} {r['sample_count']:<8}{marker}"
        )

    print(f"\n  ➜ Best day to buy {symbol}: Day {best_day} of the month")
    savings_pct = (1 - results[best_day]["avg_normalized_price"]) * 100
    if savings_pct > 0:
        print(f"    (historically {savings_pct:.3f}% below monthly average)")
    else:
        print(f"    (historically {abs(savings_pct):.3f}% above monthly average)")
    print()


def print_analysis_markdown(symbol: str, results: dict[int, dict]) -> None:
    """Print the analysis results for a single stock in Markdown format."""
    if not results:
        print(f"\n### {symbol}\n")
        print(f"> ⚠️ {symbol}: Insufficient data for analysis\n")
        return

    best_day = min(results, key=lambda d: results[d]["avg_normalized_price"])

    print(f"\n<details>")
    print(f"<summary>📈 {symbol} — Best Day of Month to Buy (Days 1–31)</summary>\n")
    print("| Day | Norm. Price | Std Dev | Avg Close ($) | Months |")
    print("|-----|-------------|---------|---------------|--------|")

    for day in TARGET_DAYS:
        if day not in results:
            continue
        r = results[day]
        marker = " ⭐" if day == best_day else ""
        print(
            f"| {day}{marker} | {r['avg_normalized_price']:.6f} | {r['std_normalized_price']:.6f}"
            f" | {r['avg_raw_price']:.2f} | {r['sample_count']} |"
        )

    savings_pct = (1 - results[best_day]["avg_normalized_price"]) * 100
    direction = "below" if savings_pct > 0 else "above"
    print(
        f"\n> 🏆 **Best day to buy {symbol}: Day {best_day}** of the month "
        f"(historically {abs(savings_pct):.3f}% {direction} monthly average)\n"
    )
    print("</details>\n")


def print_weekday_analysis(symbol: str, results: dict[int, dict]) -> None:
    """Pretty-print the best-weekday analysis results for a single symbol."""
    if not results:
        print(f"\n  {symbol}: Insufficient data for weekday analysis (need at least 3 full weeks)")
        return

    best_wd = min(results, key=lambda d: results[d]["avg_normalized_price"])

    print(f"\n{'=' * 60}")
    print(f"  {symbol} — Best Weekday to Buy")
    print(f"{'=' * 60}")
    print(f"  {'Weekday':<12} {'Norm. Price':<14} {'Std Dev':<10} {'Avg Close ($)':<16} {'Days':<8}")
    print(f"  {'-' * 56}")

    for wd in range(5):
        if wd not in results:
            continue
        r = results[wd]
        marker = " ◀ BEST" if wd == best_wd else ""
        print(
            f"  {WEEKDAY_NAMES[wd]:<12} {r['avg_normalized_price']:<14.6f} {r['std_normalized_price']:<10.6f}"
            f" {r['avg_raw_price']:<16.2f} {r['sample_count']:<8}{marker}"
        )

    savings_pct = (1 - results[best_wd]["avg_normalized_price"]) * 100
    direction = "below" if savings_pct > 0 else "above"
    print(f"\n  ➜ Best weekday to buy {symbol}: {WEEKDAY_NAMES[best_wd]}")
    print(f"    (historically {abs(savings_pct):.3f}% {direction} weekly average)\n")


def print_weekday_analysis_markdown(symbol: str, results: dict[int, dict]) -> None:
    """Print the best-weekday analysis results for a single symbol in Markdown format."""
    if not results:
        print(f"\n> ⚠️ {symbol}: Insufficient data for weekday analysis\n")
        return

    best_wd = min(results, key=lambda d: results[d]["avg_normalized_price"])

    print(f"\n<details>")
    print(f"<summary>📅 {symbol} — Best Weekday to Buy</summary>\n")
    print("| Weekday | Norm. Price | Std Dev | Avg Close ($) | Days |")
    print("|---------|-------------|---------|---------------|------|")

    for wd in range(5):
        if wd not in results:
            continue
        r = results[wd]
        marker = " ⭐" if wd == best_wd else ""
        print(
            f"| {WEEKDAY_NAMES[wd]}{marker} | {r['avg_normalized_price']:.6f}"
            f" | {r['std_normalized_price']:.6f} | {r['avg_raw_price']:.2f} | {r['sample_count']} |"
        )

    savings_pct = (1 - results[best_wd]["avg_normalized_price"]) * 100
    direction = "below" if savings_pct > 0 else "above"
    print(
        f"\n> 🏆 **Best weekday to buy {symbol}: {WEEKDAY_NAMES[best_wd]}** "
        f"(historically {abs(savings_pct):.3f}% {direction} weekly average)\n"
    )
    print("</details>\n")


def print_month_analysis(symbol: str, results: dict[int, dict]) -> None:
    """Pretty-print the best-month (seasonality) analysis results for a single symbol."""
    if not results:
        print(f"\n  {symbol}: Insufficient data for seasonality analysis (need multiple full years)")
        return

    best_month = min(results, key=lambda m: results[m]["avg_normalized_price"])

    print(f"\n{'=' * 60}")
    print(f"  {symbol} — Best Month of Year to Buy (Seasonality)")
    print(f"{'=' * 60}")
    print(f"  {'Month':<8} {'Norm. Price':<14} {'Std Dev':<10} {'Avg Close ($)':<16} {'Years':<8}")
    print(f"  {'-' * 56}")

    for month in range(1, 13):
        if month not in results:
            continue
        r = results[month]
        marker = " ◀ BEST" if month == best_month else ""
        print(
            f"  {MONTH_NAMES[month]:<8} {r['avg_normalized_price']:<14.6f} {r['std_normalized_price']:<10.6f}"
            f" {r['avg_raw_price']:<16.2f} {r['sample_count']:<8}{marker}"
        )

    savings_pct = (1 - results[best_month]["avg_normalized_price"]) * 100
    direction = "below" if savings_pct > 0 else "above"
    print(f"\n  ➜ Best month to buy {symbol}: {MONTH_NAMES[best_month]}")
    print(f"    (historically {abs(savings_pct):.3f}% {direction} yearly average)\n")


def print_month_analysis_markdown(symbol: str, results: dict[int, dict]) -> None:
    """Print the best-month (seasonality) analysis results for a single symbol in Markdown format."""
    if not results:
        print(f"\n> ⚠️ {symbol}: Insufficient data for seasonality analysis (need multiple full years)\n")
        return

    best_month = min(results, key=lambda m: results[m]["avg_normalized_price"])

    print(f"\n<details>")
    print(f"<summary>📆 {symbol} — Best Month of Year to Buy (Seasonality)</summary>\n")
    print("| Month | Norm. Price | Std Dev | Avg Close ($) | Years |")
    print("|-------|-------------|---------|---------------|-------|")

    for month in range(1, 13):
        if month not in results:
            continue
        r = results[month]
        marker = " ⭐" if month == best_month else ""
        print(
            f"| {MONTH_NAMES[month]}{marker} | {r['avg_normalized_price']:.6f}"
            f" | {r['std_normalized_price']:.6f} | {r['avg_raw_price']:.2f} | {r['sample_count']} |"
        )

    savings_pct = (1 - results[best_month]["avg_normalized_price"]) * 100
    direction = "below" if savings_pct > 0 else "above"
    print(
        f"\n> 🏆 **Best month to buy {symbol}: {MONTH_NAMES[best_month]}** "
        f"(historically {abs(savings_pct):.3f}% {direction} yearly average)\n"
    )
    print("</details>\n")
