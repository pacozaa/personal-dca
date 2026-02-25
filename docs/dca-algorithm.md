# DCA Best Buy Day Algorithm

## Overview

The `find_best_day` function (in `dca_stock/analysis.py`) determines which day of the month (1st through 7th) historically offers the lowest stock price for dollar-cost averaging (DCA) purchases.

## How It Works

### Step 1 — Parse & Sort Trading Days

The function receives a `time_series` dict (keyed by date string, values are OHLCV dicts from Alpha Vantage). It parses each entry into a `(date, closing_price)` tuple and sorts them chronologically.

```python
# Example input entry:
# "2025-03-05": {"4. close": "150.25", ...}
# → (date(2025, 3, 5), 150.25)
```

### Step 2 — Group by Month

Trading days are grouped into buckets by `(year, month)`. Months with fewer than 5 trading days are discarded as partial data (e.g., the current incomplete month or the first month in the dataset).

### Step 3 — Find the Effective Buy Price for Each Target Day

For each complete month, the algorithm checks each **target day** (1–7):

1. Construct the calendar date for that target day (e.g., January 3rd).
2. Find the **first trading day on or after** that date within the month.
   - If day 3 is a Saturday, the algorithm picks the following Monday's close.
3. Record that closing price as the "buy price" for that target day in that month.

This simulates a real DCA strategy: "I want to buy on the 3rd, but if markets are closed, I buy on the next available trading day."

### Step 4 — Normalize Prices

Raw prices aren't directly comparable across months because stock prices trend over time (a $100 close in 2020 means something different than $200 in 2025).

To solve this, each day's closing price is **normalized by the month's average closing price**:

$$
\text{normalized\_price} = \frac{\text{close\_on\_target\_day}}{\text{month\_average\_close}}
$$

A normalized value of **0.98** means the price on that day was 2% below the month's average — a relatively good day to buy. A value of **1.02** means it was 2% above average.

### Step 5 — Aggregate & Compare

For each target day (1–7), the algorithm averages the normalized prices across all months:

$$
\text{avg\_normalized\_price}(d) = \frac{1}{N} \sum_{i=1}^{N} \text{normalized\_price}_{d,i}
$$

The day with the **lowest average normalized price** is the historically best day to place a recurring DCA buy order.

## Output

The function returns a dict keyed by target day (1–7), where each value contains:

| Field                  | Description                                               |
| ---------------------- | --------------------------------------------------------- |
| `avg_normalized_price` | Mean of the normalized closing prices across all months   |
| `sample_count`         | Number of months included in the calculation              |
| `avg_raw_price`        | Simple average of the raw closing prices (for reference)  |

## Example

If the function returns:

```python
{
    1: {"avg_normalized_price": 1.003, "sample_count": 48, "avg_raw_price": 172.5},
    2: {"avg_normalized_price": 0.998, "sample_count": 48, "avg_raw_price": 171.6},
    3: {"avg_normalized_price": 0.995, "sample_count": 48, "avg_raw_price": 171.1},
    ...
}
```

Day **3** has the lowest `avg_normalized_price` (0.995), meaning that historically, buying on the 3rd of the month yielded prices about 0.5% below the monthly average — making it the best day for DCA.
