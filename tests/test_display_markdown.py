"""Tests for collapsible <details> markup in the markdown display functions."""

from __future__ import annotations

import io
import sys
from datetime import date, timedelta

import pytest

from dca_stock.analysis import find_best_day, find_best_month, find_best_weekday
from dca_stock.display import (
    print_analysis_markdown,
    print_month_analysis_markdown,
    print_weekday_analysis_markdown,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _capture(func, *args) -> str:
    """Capture stdout output from a display function call."""
    buf = io.StringIO()
    sys.stdout = buf
    try:
        func(*args)
    finally:
        sys.stdout = sys.__stdout__
    return buf.getvalue()


def _trading_days_for_month(year: int, month: int) -> list[date]:
    result = []
    d = date(year, month, 1)
    while d.month == month:
        if d.weekday() < 5:
            result.append(d)
        d += timedelta(days=1)
    return result


def _build_months(specs: list[tuple[int, int, float]]) -> dict[str, dict]:
    entries = {}
    for year, month, base in specs:
        for i, d in enumerate(_trading_days_for_month(year, month)):
            entries[d.isoformat()] = {"4. close": str(base + i * 0.1)}
    return entries


# ---------------------------------------------------------------------------
# print_analysis_markdown
# ---------------------------------------------------------------------------


class TestPrintAnalysisMarkdownCollapsible:
    def _results(self):
        ts = _build_months([(2023, m, 100 + m) for m in range(1, 13)])
        return find_best_day(ts)

    def test_opens_details_tag(self):
        output = _capture(print_analysis_markdown, "AAPL", self._results())
        assert "<details>" in output

    def test_closes_details_tag(self):
        output = _capture(print_analysis_markdown, "AAPL", self._results())
        assert "</details>" in output

    def test_summary_contains_symbol(self):
        output = _capture(print_analysis_markdown, "AAPL", self._results())
        assert "<summary>" in output
        assert "AAPL" in output
        assert "</summary>" in output

    def test_details_wraps_table(self):
        output = _capture(print_analysis_markdown, "AAPL", self._results())
        details_start = output.index("<details>")
        details_end = output.index("</details>")
        table_pos = output.index("| Day |")
        assert details_start < table_pos < details_end

    def test_no_h3_heading(self):
        """The old ### heading should no longer appear."""
        output = _capture(print_analysis_markdown, "AAPL", self._results())
        assert "### " not in output

    def test_empty_results_no_details_tag(self):
        output = _capture(print_analysis_markdown, "AAPL", {})
        assert "<details>" not in output


# ---------------------------------------------------------------------------
# print_weekday_analysis_markdown
# ---------------------------------------------------------------------------


class TestPrintWeekdayAnalysisMarkdownCollapsible:
    def _results(self):
        ts = _build_months([(2023, m, 100) for m in range(1, 13)])
        return find_best_weekday(ts)

    def test_opens_details_tag(self):
        output = _capture(print_weekday_analysis_markdown, "MSFT", self._results())
        assert "<details>" in output

    def test_closes_details_tag(self):
        output = _capture(print_weekday_analysis_markdown, "MSFT", self._results())
        assert "</details>" in output

    def test_summary_contains_symbol(self):
        output = _capture(print_weekday_analysis_markdown, "MSFT", self._results())
        assert "<summary>" in output
        assert "MSFT" in output

    def test_details_wraps_table(self):
        output = _capture(print_weekday_analysis_markdown, "MSFT", self._results())
        details_start = output.index("<details>")
        details_end = output.index("</details>")
        table_pos = output.index("| Weekday |")
        assert details_start < table_pos < details_end

    def test_no_h3_heading(self):
        output = _capture(print_weekday_analysis_markdown, "MSFT", self._results())
        assert "### " not in output

    def test_empty_results_no_details_tag(self):
        output = _capture(print_weekday_analysis_markdown, "MSFT", {})
        assert "<details>" not in output


# ---------------------------------------------------------------------------
# print_month_analysis_markdown
# ---------------------------------------------------------------------------


class TestPrintMonthAnalysisMarkdownCollapsible:
    def _results(self):
        specs = [(y, m, 100 + y * 10 + m) for y in range(2020, 2023) for m in range(1, 13)]
        ts = _build_months(specs)
        return find_best_month(ts)

    def test_opens_details_tag(self):
        output = _capture(print_month_analysis_markdown, "BTC", self._results())
        assert "<details>" in output

    def test_closes_details_tag(self):
        output = _capture(print_month_analysis_markdown, "BTC", self._results())
        assert "</details>" in output

    def test_summary_contains_symbol(self):
        output = _capture(print_month_analysis_markdown, "BTC", self._results())
        assert "<summary>" in output
        assert "BTC" in output

    def test_details_wraps_table(self):
        output = _capture(print_month_analysis_markdown, "BTC", self._results())
        details_start = output.index("<details>")
        details_end = output.index("</details>")
        table_pos = output.index("| Month |")
        assert details_start < table_pos < details_end

    def test_no_h3_heading(self):
        output = _capture(print_month_analysis_markdown, "BTC", self._results())
        assert "### " not in output

    def test_empty_results_no_details_tag(self):
        output = _capture(print_month_analysis_markdown, "BTC", {})
        assert "<details>" not in output
