# data-ingestion-pipeline

Data ingestion pipelines for pulling personal finance and trading data from external platforms into AWS S3.

## Architecture

- **Lambda** runs the ingestion (free tier)
- **EventBridge** triggers Lambda every Monday at 1am UTC (free)
- **S3** stores weekly portfolio snapshots as JSON (free tier)
- **GitHub Actions secrets** hold eToro API keys, injected into Lambda at deploy time
- **GitHub Actions** handles CI and infra deployments

## Structure

```
etoro/
  api_client.py       # Auth and raw HTTP calls to eToro
  data_sources.py     # Fetches and shapes portfolio data
  data_loader.py      # Saves snapshots to S3
  cli.py              # Local CLI for testing
infra/
  stack.py            # CDK stack — S3, Lambda, EventBridge
lambda_handler.py     # Lambda entry point
app.py                # CDK app entry point
cdk.json              # CDK config
tests/
  test_data_sources.py
```

## CI/CD Flows

| Flow | Trigger | What it does |
|------|---------|--------------|
| 🧪 Test | Every push / PR | Runs unit tests |
| 🏗️ Deploy Infra | Changes to `infra/` | Runs tests → CDK deploy |
| 📥 Ingest | Weekly (EventBridge, Mon 1am UTC) | Lambda fetches eToro data → S3 |

## Setup

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
npm install -g aws-cdk
```

### 2. Deploy infrastructure

```bash
cdk deploy
```

This provisions the S3 bucket, Lambda function, and weekly EventBridge schedule.

### 3. Add GitHub Actions secrets

In your repo settings, add:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `ETORO_PUBLIC_KEY`
- `ETORO_PRIVATE_KEY`

### 5. Test locally

```bash
cp .env.example .env  # fill in your keys
python -m etoro.cli
python -m etoro.cli --save  # saves to S3
```

## Data location

`s3://etoro-pipeline-john/portfolio/YYYY-MM-DD/snapshot.json`

## Adding a new source

Create a new top-level folder (e.g. `coinbase/`) with `api_client.py`, `data_sources.py`, `data_loader.py`, and `cli.py`. Add a new Lambda handler and EventBridge rule to `infra/stack.py`.
