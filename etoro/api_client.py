import os
import uuid
import json
import urllib.request
import urllib.error

BASE_URL = "https://public-api.etoro.com/api/v1"


def _headers():
    return {
        "x-api-key": os.getenv("ETORO_PUBLIC_KEY"),
        "x-user-key": os.getenv("ETORO_PRIVATE_KEY"),
        "x-request-id": str(uuid.uuid4()),
    }


def get(path: str) -> dict:
    req = urllib.request.Request(f"{BASE_URL}{path}", headers=_headers())
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"eToro API error {e.code}: {e.read().decode()}")
