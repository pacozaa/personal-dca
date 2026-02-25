"""Core analysis logic for finding the best DCA buy day."""

from __future__ import annotations

from collections import defaultdict
from calendar import monthrange
from datetime import date

from dca_stock.config import TARGET_DAYS


def find_best_day(time_series: dict[str, dict]) -> dict:
    """Analyze daily prices to find the best day (1-31) of the month to buy.

    For each month in the dataset, we find the first available trading day on or
    after each target day (1-31). If the target day exceeds the number of days
    in a given month (e.g. day 30 in February), it is clamped to the last day
    of that month so shorter months still contribute data. The "best" day is
    the one with the lowest average closing price across all months (normalized
    as a percentage of the month's average to account for price trends over time).

    Returns a dict with analysis results.
    """
    # Parse and sort dates
    trading_days: list[tuple[date, float]] = []
    for date_str, ohlcv in time_series.items():
        try:
            d = date.fromisoformat(date_str)
            close = float(ohlcv["4. close"])
            trading_days.append((d, close))
        except (ValueError, KeyError):
            continue

    trading_days.sort(key=lambda x: x[0])

    if not trading_days:
        return {}

    # Group trading days by (year, month)
    months: dict[tuple[int, int], list[tuple[date, float]]] = defaultdict(list)
    for d, close in trading_days:
        months[(d.year, d.month)].append((d, close))

    # For each month, find the closing price for each target day (1-7).
    # If the exact day isn't a trading day, use the first trading day on or after it.
    day_prices: dict[int, list[float]] = {day: [] for day in TARGET_DAYS}
    day_normalized: dict[int, list[float]] = {day: [] for day in TARGET_DAYS}

    for (year, month), days_in_month in months.items():
        if len(days_in_month) < 5:
            # Skip partial months (e.g. current month or data start)
            continue

        # Calculate the month's average close for normalization
        month_avg = sum(c for _, c in days_in_month) / len(days_in_month)
        if month_avg == 0:
            continue

        for target_day in TARGET_DAYS:
            # Clamp target_day to the last day of this month
            _, last_day = monthrange(year, month)
            clamped_day = min(target_day, last_day)
            target_date = date(year, month, clamped_day)

            # Find the first trading day on or after the target date
            matched_close = None
            for d, close in days_in_month:
                if d >= target_date:
                    matched_close = close
                    break

            if matched_close is not None:
                day_prices[target_day].append(matched_close)
                day_normalized[target_day].append(matched_close / month_avg)

    # Calculate statistics for each day
    results: dict[int, dict] = {}
    for day in TARGET_DAYS:
        normed = day_normalized[day]
        if normed:
            avg_normalized = sum(normed) / len(normed)
            results[day] = {
                "avg_normalized_price": avg_normalized,
                "sample_count": len(normed),
                "avg_raw_price": sum(day_prices[day]) / len(day_prices[day]),
            }

    return results
