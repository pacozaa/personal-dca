# Historical Data Fetching — `fetch_daily_prices`

## Overview

The `fetch_daily_prices` function (in `dca_stock/api.py`) is the core data-fetching layer of the project. It calls the **Alpha Vantage REST API** to retrieve daily OHLCV (Open, High, Low, Close, Volume) stock price data for a given ticker symbol.

## Function Signature

```python
def fetch_daily_prices(symbol: str, api_key: str) -> dict[str, dict]:
```

| Parameter  | Type  | Description                                      |
|------------|-------|--------------------------------------------------|
| `symbol`   | `str` | Stock ticker symbol (e.g. `"AAPL"`, `"MSFT"`)   |
| `api_key`  | `str` | Alpha Vantage API key for authentication         |
| **Return** | `dict[str, dict]` | Date-keyed dictionary of daily price data |

## Step-by-Step Walkthrough

### 1. Build the request parameters

The function constructs a query-parameter dictionary targeting the `TIME_SERIES_DAILY` endpoint:

```python
params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": symbol,
    "outputsize": "compact",
    "apikey": api_key,
}
```

- **`function`** — Tells Alpha Vantage which data series to return (daily prices).
- **`symbol`** — The stock ticker to look up.
- **`outputsize`** — `"compact"` returns the latest **100 trading days** (roughly 5 months, since weekends and holidays are excluded). The alternative `"full"` returns 20+ years of history but requires a premium API key.
- **`apikey`** — Your Alpha Vantage key.

### 2. Send the HTTP request

```python
resp = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=30)
resp.raise_for_status()
data = resp.json()
```

- A **GET** request is sent to `https://www.alphavantage.co/query` with the parameters above.
- A **30-second timeout** prevents the call from hanging indefinitely.
- `raise_for_status()` throws an exception for any HTTP-level error (4xx / 5xx).
- The JSON response is parsed into a Python dictionary.

### 3. Handle API-level errors

Alpha Vantage signals errors via special keys in the JSON body rather than HTTP status codes. The function checks three cases:

| Key             | Meaning                                               |
|-----------------|-------------------------------------------------------|
| `"Error Message"` | Invalid symbol or malformed request                 |
| `"Note"`          | API rate-limit reached (5 calls/min on free tier)   |
| `"Information"`   | General informational message (usually rate-limit)  |

If any of these keys are present, the function prints a diagnostic message and returns an **empty dict** (`{}`).

### 4. Extract the time-series data

```python
time_series = data.get("Time Series (Daily)", {})
```

On a successful response, the daily price data lives under the `"Time Series (Daily)"` key. If this key is missing or empty, the function logs a warning and returns `{}`.

### 5. Return value

The returned dictionary has this shape:

```json
{
  "2026-02-24": {
    "1. open": "185.0000",
    "2. high": "187.5000",
    "3. low": "184.2000",
    "4. close": "186.7500",
    "5. volume": "54321000"
  },
  "2026-02-21": { ... },
  ...
}
```

Each key is a **date string** (`YYYY-MM-DD`), and each value is a dict of string-valued OHLCV fields prefixed with numbers (Alpha Vantage's convention).

## Error Handling Summary

| Scenario                  | Behaviour                              |
|---------------------------|----------------------------------------|
| Network / HTTP error      | `raise_for_status()` raises exception  |
| Invalid symbol            | Returns `{}`; prints error             |
| Rate limit hit            | Returns `{}`; prints note              |
| No data in response       | Returns `{}`; prints warning           |
| Timeout (>30 s)           | `requests.Timeout` exception raised    |

## Configuration

The base URL (`https://www.alphavantage.co/query`) is imported from `dca_stock/config.py` as `ALPHA_VANTAGE_BASE_URL`, keeping the endpoint centralised and easy to change for testing or proxy setups.
