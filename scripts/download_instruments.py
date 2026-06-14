import gzip
import json
import requests

url = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz"

r = requests.get(url)

with open("/tmp/nse.json.gz", "wb") as f:
    f.write(r.content)

with gzip.open("/tmp/nse.json.gz", "rt", encoding="utf-8") as f:
    data = json.load(f)

targets = [
    "ARSS",
    "CMP",
    "NATCO",
    "SIMPLEX"
]

for item in data:

    symbol = str(item.get("trading_symbol", "")).upper()

    for target in targets:

        if target in symbol:

            print(
                symbol,
                item.get("instrument_key")
            )

