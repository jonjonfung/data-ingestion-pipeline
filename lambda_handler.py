import os
import boto3


def _load_secrets():
    ssm = boto3.client("ssm", region_name="ap-southeast-2")

    def get(name):
        return ssm.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]

    os.environ["ETORO_PUBLIC_KEY"] = get("/etoro/public_key")
    os.environ["ETORO_PRIVATE_KEY"] = get("/etoro/private_key")


def main(event, context):
    _load_secrets()

    from etoro.data_sources import fetch_portfolio
    from etoro.data_loader import save_portfolio

    data = fetch_portfolio("real")
    save_portfolio(data)

    print(f"Ingested {len(data['positions'])} positions | "
          f"Invested: ${data['total_invested']:,.2f} | "
          f"P&L: ${data['total_unrealized_pnl']:,.2f}")

    return {"status": "ok", "positions": len(data["positions"])}
