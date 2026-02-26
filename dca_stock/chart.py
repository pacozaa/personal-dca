"""Chart generation for DCA analysis results."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from dca_stock.config import MONTH_NAMES, TARGET_DAYS, WEEKDAY_NAMES

# Output directory for saved charts
_repo_root = Path(__file__).resolve().parents[1]
DATA_DIR = _repo_root / "data"


def save_chart(symbol: str, results: dict[int, dict]) -> Path | None:
    """Generate and save a bar chart showing normalized price by day of month.

    Returns the path to the saved PNG file, or None if there is no data.
    """
    if not results:
        return None

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    days = [d for d in TARGET_DAYS if d in results]
    norm_prices = [results[d]["avg_normalized_price"] for d in days]
    samples = [results[d]["sample_count"] for d in days]

    best_day = min(days, key=lambda d: results[d]["avg_normalized_price"])

    # Colours: highlight the best day
    colors = ["#2ecc71" if d == best_day else "#3498db" for d in days]

    fig, ax1 = plt.subplots(figsize=(max(10, len(days) * 0.5), 5))

    bars = ax1.bar(
        [str(d) for d in days],
        norm_prices,
        color=colors,
        edgecolor="white",
        linewidth=0.8,
    )

    # Add value labels on each bar
    label_fontsize = 7 if len(days) > 15 else 9
    for bar, price, sample in zip(bars, norm_prices, samples):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.0003,
            f"{price:.4f}",
            ha="center",
            va="bottom",
            fontsize=label_fontsize,
            fontweight="bold",
            rotation=90 if len(days) > 15 else 0,
        )
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() / 2,
            f"n={sample}",
            ha="center",
            va="center",
            fontsize=max(5, label_fontsize - 2),
            color="white",
        )

    # Reference line at 1.0 (monthly average)
    ax1.axhline(y=1.0, color="#e74c3c", linestyle="--", linewidth=1, label="Monthly avg (1.0)")

    ax1.set_xlabel("Day of Month", fontsize=11)
    ax1.set_ylabel("Avg Normalized Price", fontsize=11)
    ax1.set_title(f"{symbol} — Best Day of Month to DCA Buy", fontsize=13, fontweight="bold")
    ax1.legend(loc="upper right", fontsize=9)

    # Tighten y-axis around the data for better visibility
    y_min = min(norm_prices) - 0.002
    y_max = max(norm_prices) + 0.002
    ax1.set_ylim(y_min, y_max)

    fig.tight_layout()

    filepath = DATA_DIR / f"{symbol}_best_day.png"
    fig.savefig(filepath, dpi=150)
    plt.close(fig)

    return filepath


def save_weekday_chart(symbol: str, results: dict[int, dict]) -> Path | None:
    """Generate and save a bar chart showing normalized price by weekday (Mon–Fri).

    Returns the path to the saved PNG file, or None if there is no data.
    """
    if not results:
        return None

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    weekdays = [wd for wd in range(5) if wd in results]
    norm_prices = [results[wd]["avg_normalized_price"] for wd in weekdays]
    std_prices = [results[wd]["std_normalized_price"] for wd in weekdays]
    samples = [results[wd]["sample_count"] for wd in weekdays]
    labels = [WEEKDAY_NAMES[wd] for wd in weekdays]

    best_wd = min(weekdays, key=lambda wd: results[wd]["avg_normalized_price"])
    colors = ["#2ecc71" if wd == best_wd else "#3498db" for wd in weekdays]

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(labels, norm_prices, color=colors, edgecolor="white", linewidth=0.8, yerr=std_prices, capsize=5)

    for bar, price, sample in zip(bars, norm_prices, samples):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(std_prices) + 0.001,
            f"{price:.4f}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() / 2,
            f"n={sample}",
            ha="center",
            va="center",
            fontsize=7,
            color="white",
        )

    ax.axhline(y=1.0, color="#e74c3c", linestyle="--", linewidth=1, label="Weekly avg (1.0)")
    ax.set_xlabel("Weekday", fontsize=11)
    ax.set_ylabel("Avg Normalized Price", fontsize=11)
    ax.set_title(f"{symbol} — Best Weekday to DCA Buy", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9)

    y_min = min(p - s for p, s in zip(norm_prices, std_prices)) - 0.002
    y_max = max(p + s for p, s in zip(norm_prices, std_prices)) + 0.005
    ax.set_ylim(y_min, y_max)

    fig.tight_layout()

    filepath = DATA_DIR / f"{symbol}_best_weekday.png"
    fig.savefig(filepath, dpi=150)
    plt.close(fig)

    return filepath


def save_month_chart(symbol: str, results: dict[int, dict]) -> Path | None:
    """Generate and save a bar chart showing normalized price by calendar month (Jan–Dec).

    Returns the path to the saved PNG file, or None if there is no data.
    """
    if not results:
        return None

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    months = [m for m in range(1, 13) if m in results]
    norm_prices = [results[m]["avg_normalized_price"] for m in months]
    std_prices = [results[m]["std_normalized_price"] for m in months]
    samples = [results[m]["sample_count"] for m in months]
    labels = [MONTH_NAMES[m] for m in months]

    best_month = min(months, key=lambda m: results[m]["avg_normalized_price"])
    colors = ["#2ecc71" if m == best_month else "#3498db" for m in months]

    fig, ax = plt.subplots(figsize=(12, 5))

    bars = ax.bar(labels, norm_prices, color=colors, edgecolor="white", linewidth=0.8, yerr=std_prices, capsize=5)

    for bar, price, sample in zip(bars, norm_prices, samples):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(std_prices) + 0.001,
            f"{price:.4f}",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
        )
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() / 2,
            f"n={sample}",
            ha="center",
            va="center",
            fontsize=7,
            color="white",
        )

    ax.axhline(y=1.0, color="#e74c3c", linestyle="--", linewidth=1, label="Yearly avg (1.0)")
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Avg Normalized Price", fontsize=11)
    ax.set_title(f"{symbol} — Best Month of Year to DCA Buy (Seasonality)", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9)

    if norm_prices:
        y_min = min(p - s for p, s in zip(norm_prices, std_prices)) - 0.002
        y_max = max(p + s for p, s in zip(norm_prices, std_prices)) + 0.005
        ax.set_ylim(y_min, y_max)

    fig.tight_layout()

    filepath = DATA_DIR / f"{symbol}_best_month.png"
    fig.savefig(filepath, dpi=150)
    plt.close(fig)

    return filepath


def save_summary_chart(overall_best: dict[str, int], all_results: dict[str, dict[int, dict]]) -> Path | None:
    """Generate and save a grouped summary chart for all analysed stocks.

    Returns the path to the saved PNG file, or None if there is no data.
    """
    if not all_results:
        return None

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    symbols = list(all_results.keys())
    # Only include days that have data for at least one symbol
    days = sorted({d for res in all_results.values() for d in res})

    n_days = len(days)
    group_width = 0.8  # total width allocated per symbol group
    bar_width = group_width / max(n_days, 1)
    fig, ax = plt.subplots(figsize=(max(10, len(symbols) * 4), 6))

    x_positions = range(len(symbols))

    for i, day in enumerate(days):
        values = []
        for sym in symbols:
            res = all_results[sym]
            values.append(res[day]["avg_normalized_price"] if day in res else None)

        offsets = [x + i * bar_width for x in x_positions]
        valid_offsets = [o for o, v in zip(offsets, values) if v is not None]
        valid_values = [v for v in values if v is not None]

        ax.bar(
            valid_offsets,
            valid_values,
            width=bar_width,
            label=f"Day {day}",
        )

    ax.axhline(y=1.0, color="#e74c3c", linestyle="--", linewidth=1, label="Monthly avg")
    ax.set_xlabel("Stock", fontsize=11)
    ax.set_ylabel("Avg Normalized Price", fontsize=11)
    ax.set_title("DCA Best Buy Day — All Stocks", fontsize=13, fontweight="bold")
    ax.set_xticks([x + bar_width * (len(days) - 1) / 2 for x in x_positions])
    ax.set_xticklabels(symbols, fontsize=10)
    ax.legend(fontsize=7, ncol=min(len(days), 10), loc="upper center", bbox_to_anchor=(0.5, -0.15))

    fig.tight_layout()

    filepath = DATA_DIR / "summary_best_day.png"
    fig.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return filepath

