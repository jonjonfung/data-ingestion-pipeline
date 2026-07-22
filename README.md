# data-ingestion-pipeline

Data ingestion pipelines for pulling personal finance and trading data from external platforms into AWS S3.

## Structure

```
etoro/
  api_client.py     # Auth and raw HTTP calls to eToro
  data_sources.py   # Fetches and shapes data (portfolio, positions, P&L)
  data_loader.py    # Saves data to S3
  cli.py            # Command line entry point
infra/
  s3_stack.py       # AWS CDK stack — provisions the S3 bucket
```

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your eToro API keys:
   ```
   ETORO_PUBLIC_KEY=your_public_key
   ETORO_PRIVATE_KEY=your_private_key
   ```
   Get your keys from eToro: Settings > Trading > API Key Management

3. Deploy the S3 bucket (first time only):
   ```bash
   cdk deploy
   ```

## Usage

```bash
# Print portfolio summary
python -m etoro.cli

# Print and save snapshot to S3
python -m etoro.cli --save

# Use demo account
python -m etoro.cli --account demo
```

Data is saved to: `s3://etoro-pipeline-john/portfolio/YYYY-MM-DD/snapshot.json`

## Adding a new source

Create a new top-level folder (e.g. `coinbase/`) with the same structure: `api_client.py`, `data_sources.py`, `data_loader.py`, `cli.py`.
