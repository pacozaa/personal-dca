# Personal DCA

A Python project for Dollar Cost Averaging strategies.

## Project Structure

```
personal-dca/
├── pyproject.toml          # Project configuration
├── dca_stock/              # Stock DCA module
│   ├── __init__.py
│   ├── analyze.py          # CLI entry point
│   ├── analysis.py         # Core analysis logic
│   ├── api.py              # Alpha Vantage API client
│   ├── chart.py            # Chart generation
│   ├── config.py           # Configuration & env loading
│   └── display.py          # Output formatting
├── tests/
│   └── test_analysis.py    # Unit tests for analysis functions
└── docs/
    ├── dca-algorithm.md          # Best day-of-month algorithm
    ├── weekday-analysis.md       # Best weekday algorithm
    ├── seasonality-analysis.md   # Best month-of-year algorithm
    ├── history-data-details.md
    └── github-action-secrets.md
```

## Requirements

- Python 3.13.5

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Run the DCA stock analysis:

```bash
# Via module
python -m dca_stock.analyze

# Or via installed script
dca-stock-analyze
```

## What It Analyses

For each stock / crypto symbol the tool runs **three complementary analyses**:

| Analysis | Question answered | Output |
|---|---|---|
| **Best day of month** (Days 1–31) | Which calendar date is historically cheapest? | Table + bar chart per symbol + summary chart |
| **Best weekday** (Mon–Fri) | Which day of the week is historically cheapest? | Table + bar chart with error bars per symbol |
| **Best month of year** (Jan–Dec) | Which season is historically cheapest? | Table + bar chart with error bars per symbol |

Every table includes a **Std Dev** column so you can see how *consistent* (reliable) the pattern is — a low standard deviation means the signal is more trustworthy.

> **Note:** Seasonality analysis requires multiple **full years** of price history. With the free Alpha Vantage tier (`outputsize=compact`, ~100 trading days ≈ 5 months) only the day-of-month and weekday analyses will be populated. Use a premium key to fetch full history and unlock seasonality results.

## Output Formats

```bash
# Plain text (default)
dca-stock-analyze

# GitHub-flavoured Markdown (great for CI step summaries)
dca-stock-analyze --output-format markdown
```

## Charts

All charts are saved to the `data/` directory:

| File | Description |
|---|---|
| `{SYMBOL}_best_day.png` | Normalized price by day of month |
| `{SYMBOL}_best_weekday.png` | Normalized price by weekday (with std dev error bars) |
| `{SYMBOL}_best_month.png` | Normalized price by month of year (with std dev error bars) |
| `summary_best_day.png` | Grouped comparison across all symbols |

