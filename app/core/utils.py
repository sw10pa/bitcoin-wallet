from typing import Optional

import requests


def get_btc_to_usd_rate() -> Optional[float]:
    url = "https://api.coindesk.com/v1/bpi/currentprice/USD.json"
    result = None
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = float(response.json()["bpi"]["USD"]["rate_float"])
    except Exception as e:
        print("Error getting BTC to USD rate", e)
    return result
