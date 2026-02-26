"""Tests for dca_stock.analysis — find_best_day, find_best_weekday, find_best_month."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from dca_stock.analysis import find_best_day, find_best_month, find_best_weekday

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_time_series(entries: list[tuple[date, float]]) -> dict[str, dict]:
    """Build a minimal time_series dict from (date, close) pairs."""
    return {d.isoformat(): {"4. close": str(close)} for d, close in entries}


def _trading_days_for_month(year: int, month: int) -> list[date]:
    """Return Mon–Fri dates for a given (year, month)."""
    result = []
    d = date(year, month, 1)
    while d.month == month:
        if d.weekday() < 5:
            result.append(d)
        d += timedelta(days=1)
    return result


def _build_months(specs: list[tuple[int, int, float]]) -> dict[str, dict]:
    """Build a time_series from (year, month, base_price) specs.

    Within each month, prices ramp slightly so the month has a meaningful average.
    """
    entries = []
    for year, month, base in specs:
        days = _trading_days_for_month(year, month)
        for i, d in enumerate(days):
            entries.append((d, base + i * 0.1))
    return _make_time_series(entries)


# ---------------------------------------------------------------------------
# find_best_day
# ---------------------------------------------------------------------------


class TestFindBestDay:
    def test_empty_input(self):
        assert find_best_day({}) == {}

    def test_bad_data_skipped(self):
        ts = {"2024-01-15": {"no_close": "100"}}
        assert find_best_day(ts) == {}

    def test_returns_all_days_with_data(self):
        # Build 12 full months so all days 1-31 can be found
        ts = _build_months([(2023, m, 100 + m) for m in range(1, 13)])
        results = find_best_day(ts)
        assert len(results) > 0
        for day_data in results.values():
            assert "avg_normalized_price" in day_data
            assert "std_normalized_price" in day_data
            assert "sample_count" in day_data
            assert "avg_raw_price" in day_data

    def test_std_normalized_price_non_negative(self):
        ts = _build_months([(2023, m, 150) for m in range(1, 13)])
        results = find_best_day(ts)
        for day_data in results.values():
            assert day_data["std_normalized_price"] >= 0

    def test_normalized_price_near_one(self):
        """Normalized prices must be close to 1.0 (since they are fractions of the monthly avg)."""
        ts = _build_months([(2022, m, 200 + m * 5) for m in range(1, 13)])
        results = find_best_day(ts)
        for day_data in results.values():
            assert 0.8 < day_data["avg_normalized_price"] < 1.2

    def test_uniform_prices_normalized_to_one(self):
        """When every trading day has the same close price, normalized price == 1.0."""
        jan_days = _trading_days_for_month(2024, 1)
        ts = _make_time_series([(d, 100.0) for d in jan_days])
        results = find_best_day(ts)
        for day_data in results.values():
            assert day_data["avg_normalized_price"] == pytest.approx(1.0)

    def test_lower_price_day_has_lower_normalized_price(self):
        """A day with lower price should have lower normalized price than a day with higher price."""
        jan_days = _trading_days_for_month(2024, 1)
        prices = {d: 100.0 for d in jan_days}
        prices[jan_days[0]] = 50.0   # Jan 2 → target day 1 resolves here (cheap)
        prices[jan_days[9]] = 200.0  # Jan 15 → target day 15 resolves here (expensive)
        ts = _make_time_series([(d, prices[d]) for d in jan_days])
        results = find_best_day(ts)
        assert results[1]["avg_normalized_price"] < results[15]["avg_normalized_price"]

    def test_insufficient_months_skipped(self):
        """Months with fewer than 5 trading days should be skipped."""
        # Create a series with only 2 trading days in a month
        entries = [(date(2024, 1, 2), 100.0), (date(2024, 1, 3), 101.0)]
        ts = _make_time_series(entries)
        results = find_best_day(ts)
        assert results == {}


# ---------------------------------------------------------------------------
# find_best_day — day clamping
# ---------------------------------------------------------------------------


class TestFindBestDayClamping:
    """Verify that target days beyond the month length are clamped correctly."""

    def test_day_30_and_31_clamped_to_last_feb_day(self):
        """Days 30 and 31 in a 29-day month must clamp to day 29."""
        feb_days = _trading_days_for_month(2024, 2)  # Feb 2024 is a leap year (29 days)
        ts = _make_time_series([(d, 100.0) for d in feb_days])
        results = find_best_day(ts)
        assert results[30]["avg_raw_price"] == pytest.approx(results[29]["avg_raw_price"])
        assert results[31]["avg_raw_price"] == pytest.approx(results[29]["avg_raw_price"])


# ---------------------------------------------------------------------------
# find_best_weekday
# ---------------------------------------------------------------------------


class TestFindBestWeekday:
    def test_empty_input(self):
        assert find_best_weekday({}) == {}

    def test_returns_five_weekdays(self):
        ts = _build_months([(2023, m, 100) for m in range(1, 13)])
        results = find_best_weekday(ts)
        # Should have data for all 5 weekdays (Mon-Fri)
        assert len(results) == 5
        assert set(results.keys()) == {0, 1, 2, 3, 4}

    def test_result_fields_present(self):
        ts = _build_months([(2023, m, 100) for m in range(1, 13)])
        results = find_best_weekday(ts)
        for wd_data in results.values():
            assert "avg_normalized_price" in wd_data
            assert "std_normalized_price" in wd_data
            assert "sample_count" in wd_data
            assert "avg_raw_price" in wd_data

    def test_normalized_price_near_one(self):
        ts = _build_months([(2023, m, 200) for m in range(1, 13)])
        results = find_best_weekday(ts)
        for wd_data in results.values():
            assert 0.9 < wd_data["avg_normalized_price"] < 1.1

    def test_std_non_negative(self):
        ts = _build_months([(2023, m, 100) for m in range(1, 13)])
        results = find_best_weekday(ts)
        for wd_data in results.values():
            assert wd_data["std_normalized_price"] >= 0

    def test_partial_weeks_skipped(self):
        """A week with only 2 trading days should be excluded."""
        # Only Monday and Tuesday in a single week
        entries = [(date(2024, 1, 1), 100.0), (date(2024, 1, 2), 101.0)]
        ts = _make_time_series(entries)
        results = find_best_weekday(ts)
        assert results == {}


# ---------------------------------------------------------------------------
# find_best_month
# ---------------------------------------------------------------------------


class TestFindBestMonth:
    def test_empty_input(self):
        assert find_best_month({}) == {}

    def test_insufficient_years_returns_empty(self):
        """With only 1 partial year, result should be empty (< 200 trading days threshold)."""
        ts = _build_months([(2023, m, 100) for m in range(1, 7)])  # 6 months only
        results = find_best_month(ts)
        assert results == {}

    def test_returns_twelve_months_with_full_years(self):
        # Build 3 full years (2020, 2021, 2022)
        specs = [(y, m, 100 + y * 10 + m) for y in range(2020, 2023) for m in range(1, 13)]
        ts = _build_months(specs)
        results = find_best_month(ts)
        assert len(results) == 12
        assert set(results.keys()) == set(range(1, 13))

    def test_result_fields_present(self):
        specs = [(y, m, 100 + y * 5) for y in range(2020, 2023) for m in range(1, 13)]
        ts = _build_months(specs)
        results = find_best_month(ts)
        for month_data in results.values():
            assert "avg_normalized_price" in month_data
            assert "std_normalized_price" in month_data
            assert "sample_count" in month_data
            assert "avg_raw_price" in month_data

    def test_normalized_price_near_one(self):
        specs = [(y, m, 200 + y * 20 + m) for y in range(2020, 2025) for m in range(1, 13)]
        ts = _build_months(specs)
        results = find_best_month(ts)
        for month_data in results.values():
            assert 0.8 < month_data["avg_normalized_price"] < 1.2

    def test_sample_count_equals_number_of_years(self):
        """Each month's sample_count should equal the number of full years in the data."""
        n_years = 4
        specs = [(y, m, 100) for y in range(2020, 2020 + n_years) for m in range(1, 13)]
        ts = _build_months(specs)
        results = find_best_month(ts)
        for month_data in results.values():
            assert month_data["sample_count"] == n_years

    def test_seasonality_detected(self):
        """If January is consistently cheaper, it should have the lowest normalized price."""
        specs = []
        for year in range(2018, 2023):
            for month in range(1, 13):
                # January is priced at 80 while all others are 120
                base_price = 80.0 if month == 1 else 120.0
                specs.append((year, month, base_price))
        ts = _build_months(specs)
        results = find_best_month(ts)
        best_month = min(results, key=lambda m: results[m]["avg_normalized_price"])
        assert best_month == 1  # January should win
