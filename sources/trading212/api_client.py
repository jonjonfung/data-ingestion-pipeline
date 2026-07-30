import os
import json
import base64
import urllib.request
import urllib.error

BASE_URL = "https://live.trading212.com"


def _headers():
    key = os.getenv("TRADING212_API_KEY")
    secret = os.getenv("TRADING212_API_SECRET")
    credentials = base64.b64encode(f"{key}:{secret}".encode()).decode()
    return {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
    }


def get(path: str) -> dict | list:
    req = urllib.request.Request(f"{BASE_URL}{path}", headers=_headers())
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Trading212 API error {e.code}: {e.read().decode()}")
