# Best Weekday to Buy — Algorithm

## Overview

The `find_best_weekday` function (in `dca_stock/analysis.py`) determines which day of the
trading week (Monday through Friday) historically offers the lowest closing price for DCA
purchases.

## How It Works

### Step 1 — Parse & Sort Trading Days

Same as the day-of-month analysis: the input `time_series` dict is parsed into
`(date, closing_price)` tuples and sorted chronologically.

### Step 2 — Group by ISO Week

Trading days are grouped into **ISO calendar weeks** (year + week number). Weeks with
fewer than **3 trading days** are discarded as holiday or partial weeks — for example,
the week of Thanksgiving or the very first/last week in the dataset.

### Step 3 — Normalize by Week Average

Within each qualifying week, each day's closing price is normalized by the **week's
average closing price**:

$$
\text{normalized\_price} = \frac{\text{close\_on\_weekday}}{\text{week\_average\_close}}
$$

This removes the effect of long-term price trends: a Monday close of $100 in 2020 is
treated the same as a Monday close of $200 in 2025 — both are expressed relative to
their own week's average.

### Step 4 — Aggregate & Compare

For each weekday (0 = Monday … 4 = Friday) the normalized prices are averaged across
all qualifying weeks. The weekday with the **lowest average normalized price** is the
historically best day to place a recurring DCA buy order.

A **standard deviation** is also computed for each weekday so you can see how
*consistent* the signal is — lower std means the pattern is more reliable.

## Output

The function returns a dict keyed by weekday integer (0–4), where each value contains:

| Field                  | Description                                                        |
| ---------------------- | ------------------------------------------------------------------ |
| `avg_normalized_price` | Mean of normalized closing prices across all qualifying weeks      |
| `std_normalized_price` | Standard deviation — lower means a more consistent weekday pattern |
| `sample_count`         | Total number of individual trading days included                   |
| `avg_raw_price`        | Simple average of raw closing prices (for reference)               |

## Data Requirements

Weekday analysis works well with the free Alpha Vantage tier (`outputsize=compact`,
~100 trading days ≈ 20 weeks), giving roughly **20 data points per weekday** — enough
for a preliminary signal.
