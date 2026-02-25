# GitHub Action Secrets Setup

The **Daily DCA Stock Analysis** workflow requires at least one asset list (`DCA_STOCKS` and/or `DCA_CRYPTO`) and the API key to be configured in your GitHub repository.

## Required Secrets

| Secret Name            | Description                                        | Example Value        |
| ---------------------- | -------------------------------------------------- | -------------------- |
| `ALPHAVANTAGE_API_KEY` | API key from Alpha Vantage for fetching price data  | `A1B2C3D4E5F6G7H8` |

## Optional Secrets (at least one required)

| Secret Name   | Description                                          | Example Value      |
| ------------- | ---------------------------------------------------- | ------------------ |
| `DCA_STOCKS`  | Comma-separated list of stock ticker symbols         | `AAPL,MSFT,GOOGL`  |
| `DCA_CRYPTO`  | Comma-separated list of cryptocurrency symbols       | `BTC,ETH`          |

## How to Add Secrets

Make sure you have the [GitHub CLI](https://cli.github.com/) installed and authenticated (`gh auth login`).

```bash
gh secret set ALPHAVANTAGE_API_KEY --body "your-api-key-here"
gh secret set DCA_STOCKS --body "AAPL,MSFT,GOOGL"
gh secret set DCA_CRYPTO --body "BTC,ETH"
```

To verify the secrets were added:

```bash
gh secret list
```

## Getting an Alpha Vantage API Key

1. Visit [https://www.alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)
2. Fill in the form and click **GET FREE API KEY**
3. Copy the key and save it as the `ALPHAVANTAGE_API_KEY` secret

## Verifying the Setup

After adding both secrets, you can trigger the workflow manually:

1. Go to the **Actions** tab in your repository
2. Select **Daily DCA Stock Analysis** from the left sidebar
3. Click **Run workflow** → **Run workflow**
4. Check the run output and job summary to confirm everything works
