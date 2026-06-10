import os
import requests

INSTRUMENTS = {
    "BEL": "NSE_EQ|INE263A01024",
}

UPSTOX_ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")


def get_profile():
    response = requests.get(
        "https://api.upstox.com/v2/user/profile",
        headers={
            "Authorization": f"Bearer {UPSTOX_ACCESS_TOKEN}",
            "Accept": "application/json"
        }
    )

    return response.json()


def get_candles(symbol):
    instrument_key = INSTRUMENTS.get(symbol.upper())

    return {
        "symbol": symbol,
        "instrument_key": instrument_key,
        "url": f"https://api.upstox.com/v2/historical-candle/{instrument_key}/day"
    }


def search_instrument(query):
    return {
        "query": query,
        "message": "Search endpoint temporarily disabled for debugging"
    }

