from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class Response:
    success: bool
    message: str


def get_btc_to_usd_rate() -> Optional[float]:
    url = "https://api.coindesk.com/v1/bpi/currentprice/USD.json"
    response = requests.get(url)
    if response.status_code == 200:
        return float(response.json()["bpi"]["USD"]["rate_float"])
    else:
        return None
