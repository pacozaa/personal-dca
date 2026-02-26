"""Unit tests for dca_stock.analysis.find_best_day."""

from __future__ import annotations

import pytest

from dca_stock.analysis import find_best_day


def _make_time_series(entries: list[tuple[str, float]]) -> dict[str, dict]:
    """Build a minimal time-series dict accepted by find_best_day."""
    return {date_str: {"4. close": str(close)} for date_str, close in entries}


class TestFindBestDayEmptyInput:
    def test_empty_dict_returns_empty(self):
        assert find_best_day({}) == {}

    def test_all_malformed_entries_returns_empty(self):
        ts = {
            "not-a-date": {"4. close": "100.0"},
            "2024-01-15": {"wrong_key": "100.0"},
        }
        assert find_best_day(ts) == {}


class TestFindBestDayPartialMonth:
    def test_partial_month_is_skipped(self):
        """Months with fewer than 5 trading days must be skipped."""
        # Only 3 trading days in Jan 2024 → should be skipped → empty result
        ts = _make_time_series(
            [
                ("2024-01-02", 100.0),
                ("2024-01-03", 101.0),
                ("2024-01-04", 102.0),
            ]
        )
        assert find_best_day(ts) == {}


class TestFindBestDayFullMonth:
    # Build a full month (Jan 2024 weekdays: 2,3,4,5,8,9,...,31 → 22 trading days)
    _JAN_2024_DAYS = [
        "2024-01-02",
        "2024-01-03",
        "2024-01-04",
        "2024-01-05",
        "2024-01-08",
        "2024-01-09",
        "2024-01-10",
        "2024-01-11",
        "2024-01-12",
        "2024-01-15",
        "2024-01-16",
        "2024-01-17",
        "2024-01-18",
        "2024-01-19",
        "2024-01-22",
        "2024-01-23",
        "2024-01-24",
        "2024-01-25",
        "2024-01-26",
        "2024-01-29",
        "2024-01-30",
        "2024-01-31",
    ]

    def _ts(self, prices: list[float]) -> dict[str, dict]:
        assert len(prices) == len(self._JAN_2024_DAYS)
        return _make_time_series(list(zip(self._JAN_2024_DAYS, prices)))

    def test_returns_dict_keyed_by_day(self):
        ts = self._ts([float(100 + i) for i in range(len(self._JAN_2024_DAYS))])
        result = find_best_day(ts)
        assert isinstance(result, dict)
        # All 31 target days should be present (each resolves to the first trading day ≥ target)
        for day in range(1, 32):
            assert day in result, f"Day {day} missing from result"

    def test_result_fields_present(self):
        ts = self._ts([100.0] * len(self._JAN_2024_DAYS))
        result = find_best_day(ts)
        for day, stats in result.items():
            assert "avg_normalized_price" in stats, f"Missing avg_normalized_price for day {day}"
            assert "sample_count" in stats, f"Missing sample_count for day {day}"
            assert "avg_raw_price" in stats, f"Missing avg_raw_price for day {day}"

    def test_uniform_prices_normalized_to_one(self):
        """When every trading day has the same close price, normalized price == 1.0."""
        ts = self._ts([100.0] * len(self._JAN_2024_DAYS))
        result = find_best_day(ts)
        for day, stats in result.items():
            assert stats["avg_normalized_price"] == pytest.approx(1.0), (
                f"Day {day}: expected normalized price 1.0, got {stats['avg_normalized_price']}"
            )

    def test_lower_price_day_has_lower_normalized_price(self):
        """A day with a known lower price should have a lower normalized price than a higher one."""
        # Make day 2 (2024-01-02) cheap and day 15 (2024-01-15) expensive
        prices = [100.0] * len(self._JAN_2024_DAYS)
        prices[0] = 50.0   # 2024-01-02 → target day 1 and 2 will resolve here
        prices[9] = 200.0  # 2024-01-15 → target day 15

        ts = self._ts(prices)
        result = find_best_day(ts)

        assert result[1]["avg_normalized_price"] < result[15]["avg_normalized_price"]

    def test_sample_count_is_positive(self):
        ts = self._ts([100.0] * len(self._JAN_2024_DAYS))
        result = find_best_day(ts)
        for day, stats in result.items():
            assert stats["sample_count"] >= 1, f"Day {day} has sample_count < 1"


class TestFindBestDayDayClamping:
    """Verify that target days beyond the month length are clamped correctly."""

    # February 2024 (leap year: 29 days); use ≥5 weekday trading days
    _FEB_2024_DAYS = [
        "2024-02-01",
        "2024-02-02",
        "2024-02-05",
        "2024-02-06",
        "2024-02-07",
        "2024-02-08",
        "2024-02-09",
        "2024-02-12",
        "2024-02-13",
        "2024-02-14",
        "2024-02-15",
        "2024-02-16",
        "2024-02-20",
        "2024-02-21",
        "2024-02-22",
        "2024-02-23",
        "2024-02-26",
        "2024-02-27",
        "2024-02-28",
        "2024-02-29",
    ]

    def _ts(self, prices: list[float]) -> dict[str, dict]:
        assert len(prices) == len(self._FEB_2024_DAYS)
        return _make_time_series(list(zip(self._FEB_2024_DAYS, prices)))

    def test_day_30_and_31_clamped_to_last_feb_day(self):
        """Days 30 and 31 in a 29-day month must clamp to day 29."""
        ts = self._ts([100.0] * len(self._FEB_2024_DAYS))
        result = find_best_day(ts)
        # Both day 30 and day 31 should resolve to the same trading day as day 29
        assert result[30]["avg_raw_price"] == pytest.approx(result[29]["avg_raw_price"])
        assert result[31]["avg_raw_price"] == pytest.approx(result[29]["avg_raw_price"])
