import os
import uuid
import requests

BASE_URL = "https://public-api.etoro.com/api/v1"


def _headers():
    return {
        "x-api-key": os.getenv("ETORO_PUBLIC_KEY"),
        "x-user-key": os.getenv("ETORO_PRIVATE_KEY"),
        "x-request-id": str(uuid.uuid4()),
    }


def get(path: str) -> dict:
    response = requests.get(f"{BASE_URL}{path}", headers=_headers())
    response.raise_for_status()
    return response.json()
