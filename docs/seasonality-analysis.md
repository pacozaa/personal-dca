# Best Month of Year to Buy — Seasonality Algorithm

## Overview

The `find_best_month` function (in `dca_stock/analysis.py`) identifies which calendar
month (January through December) historically offers the lowest average closing price for
DCA purchases — i.e., it detects **seasonal patterns** in stock and crypto prices.

## How It Works

### Step 1 — Parse & Sort Trading Days

Same as the other analyses: the input `time_series` dict is parsed into
`(date, closing_price)` tuples and sorted chronologically.

### Step 2 — Group by Year, then by Month

Trading days are first grouped by **calendar year**. Years with fewer than **200 trading
days** are discarded as partial years (roughly 10 months of data minimum — a full trading
year has ~252 days).

Within each qualifying year, trading days are then grouped by **calendar month**.

### Step 3 — Compute Monthly Averages and Normalize

For each month within a qualifying year:

1. Calculate the **monthly average closing price** (mean of all daily closes in that month).
2. Normalize it by the **year's overall average closing price**:

$$
\text{normalized\_monthly\_price} = \frac{\text{monthly\_avg\_close}}{\text{yearly\_avg\_close}}
$$

This removes the long-term upward trend: a January average of $50 in 2015 is treated the
same as a January average of $150 in 2024 — both are expressed relative to their own
year's average.

Months with fewer than **10 trading days** within a year are skipped (e.g., partial
months at the data boundary).

### Step 4 — Aggregate & Compare

For each calendar month (1 = January … 12 = December), the normalized prices are averaged
across all qualifying years. The month with the **lowest average normalized price** is the
historically best month to concentrate DCA purchases.

A **standard deviation** is also computed to quantify how consistently the pattern
repeats year-over-year.

## Output

The function returns a dict keyed by month integer (1–12), where each value contains:

| Field                  | Description                                                         |
| ---------------------- | ------------------------------------------------------------------- |
| `avg_normalized_price` | Mean of normalized monthly prices across all qualifying years       |
| `std_normalized_price` | Standard deviation — lower means a more consistent seasonal pattern |
| `sample_count`         | Number of years that contributed data for this month                |
| `avg_raw_price`        | Simple average of raw monthly average prices (for reference)        |

## Data Requirements

Seasonality analysis requires **multiple full calendar years** of price history. With the
free Alpha Vantage tier (`outputsize=compact`, ~100 trading days ≈ 5 months), no complete
years are available and the function will return an empty dict.

To unlock seasonality results:
- Use a **premium Alpha Vantage key** and set `outputsize=full` in `api.py` to fetch
  20+ years of history.
- A minimum of **2–3 full years** is recommended for a meaningful signal. The more years,
  the more reliable the seasonal pattern.
