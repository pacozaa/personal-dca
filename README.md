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
│   ├── config.py           # Configuration & env loading
│   └── display.py          # Output formatting
└── tests/
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
