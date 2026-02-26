"""Core analysis logic for finding the best DCA buy day."""

from __future__ import annotations

import math
from calendar import monthrange
from collections import defaultdict
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

    Returns a dict with analysis results, keyed by day (1-31).
    Each entry contains:
      - avg_normalized_price: mean normalized price
      - std_normalized_price: standard deviation of normalized price (lower = more consistent)
      - sample_count: number of months with data
      - avg_raw_price: mean raw closing price
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
            variance = sum((x - avg_normalized) ** 2 for x in normed) / len(normed)
            results[day] = {
                "avg_normalized_price": avg_normalized,
                "std_normalized_price": math.sqrt(variance),
                "sample_count": len(normed),
                "avg_raw_price": sum(day_prices[day]) / len(day_prices[day]),
            }

    return results


def find_best_weekday(time_series: dict[str, dict]) -> dict:
    """Analyze which weekday (Monday–Friday) historically has the lowest average price.

    Prices are normalized by the ISO week's average closing price to remove
    long-term price trends. Returns a dict keyed by weekday integer (0=Monday,
    4=Friday). Each entry contains:
      - avg_normalized_price: mean normalized price for that weekday
      - std_normalized_price: standard deviation (lower = more consistent)
      - sample_count: number of individual trading days sampled
      - avg_raw_price: mean raw closing price
    """
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

    # Group by ISO week (year, week_number)
    weeks: dict[tuple[int, int], list[tuple[date, float]]] = defaultdict(list)
    for d, close in trading_days:
        iso_year, iso_week, _ = d.isocalendar()
        weeks[(iso_year, iso_week)].append((d, close))

    weekday_prices: dict[int, list[float]] = {wd: [] for wd in range(5)}
    weekday_normalized: dict[int, list[float]] = {wd: [] for wd in range(5)}

    for _, days_in_week in weeks.items():
        if len(days_in_week) < 3:
            # Skip weeks with fewer than 3 trading days (holiday weeks, partial weeks)
            continue

        week_avg = sum(c for _, c in days_in_week) / len(days_in_week)
        if week_avg == 0:
            continue

        for d, close in days_in_week:
            wd = d.weekday()
            if wd < 5:  # Mon–Fri only
                weekday_prices[wd].append(close)
                weekday_normalized[wd].append(close / week_avg)

    results: dict[int, dict] = {}
    for wd in range(5):
        normed = weekday_normalized[wd]
        if normed:
            avg_normalized = sum(normed) / len(normed)
            variance = sum((x - avg_normalized) ** 2 for x in normed) / len(normed)
            results[wd] = {
                "avg_normalized_price": avg_normalized,
                "std_normalized_price": math.sqrt(variance),
                "sample_count": len(normed),
                "avg_raw_price": sum(weekday_prices[wd]) / len(weekday_prices[wd]),
            }

    return results


def find_best_month(time_series: dict[str, dict]) -> dict:
    """Analyze which calendar month (Jan–Dec) historically has the lowest average price.

    For each complete year in the dataset, each month's average closing price is
    normalized by that year's average closing price to remove the long-term upward
    trend. Returns a dict keyed by month integer (1=Jan, 12=Dec). Each entry:
      - avg_normalized_price: mean normalized monthly price across all years
      - std_normalized_price: standard deviation (lower = more consistent pattern)
      - sample_count: number of years that contributed data for this month
      - avg_raw_price: mean raw monthly average closing price
    """
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

    # Group by year
    years: dict[int, list[tuple[date, float]]] = defaultdict(list)
    for d, close in trading_days:
        years[d.year].append((d, close))

    month_avg_prices: dict[int, list[float]] = {m: [] for m in range(1, 13)}
    month_normalized: dict[int, list[float]] = {m: [] for m in range(1, 13)}

    for _, days_in_year in years.items():
        if len(days_in_year) < 200:
            # Skip partial years (< ~10 months of trading days)
            continue

        year_avg = sum(c for _, c in days_in_year) / len(days_in_year)
        if year_avg == 0:
            continue

        # Group by month within this year
        month_groups: dict[int, list[float]] = defaultdict(list)
        for d, close in days_in_year:
            month_groups[d.month].append(close)

        for month, closes in month_groups.items():
            if len(closes) < 10:
                # Skip months with very few trading days (e.g. partial month at data boundary)
                continue
            monthly_avg = sum(closes) / len(closes)
            month_avg_prices[month].append(monthly_avg)
            month_normalized[month].append(monthly_avg / year_avg)

    results: dict[int, dict] = {}
    for month in range(1, 13):
        normed = month_normalized[month]
        if normed:
            avg_normalized = sum(normed) / len(normed)
            variance = sum((x - avg_normalized) ** 2 for x in normed) / len(normed)
            results[month] = {
                "avg_normalized_price": avg_normalized,
                "std_normalized_price": math.sqrt(variance),
                "sample_count": len(normed),
                "avg_raw_price": sum(month_avg_prices[month]) / len(month_avg_prices[month]),
            }

    return results
