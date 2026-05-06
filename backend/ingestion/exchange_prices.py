import requests
from datetime import datetime
from zoneinfo import ZoneInfo

BRT = ZoneInfo('America/Sao_Paulo')

def fill_exchange_info(exchange, ask, bid, taker_fee_pct) -> dict:
    ask = float(ask)
    bid = float(bid)
    spread = ask - bid
    spread_pct = spread/bid * 100

    result = {
        "exchange" : exchange,
        "ask_brl" : ask,
        "bid_brl" : bid,
        "spread" : spread,
        "spread_pct": spread_pct,
        "taker_fee_pct": taker_fee_pct,
        "datetime" : datetime.now(BRT).replace(tzinfo=None)
    }

    return result

def fetch_mercado_bitcoin() -> dict | None:
    try:
        response = requests.get("https://www.mercadobitcoin.net/api/BTC/ticker/", timeout=10)
        response.raise_for_status()
        data = response.json()

        ask = data['ticker']['sell']
        bid = data['ticker']['buy']
        result = fill_exchange_info("mercado_bitcoin", ask, bid, 0.07)
        
        return result

    except Exception as e:
        print(f"Erro ao buscar Mercado Bitcoin: {e}")
        return None
    
def fetch_nova_dax() -> dict | None:
    try: 
        response = requests.get("https://api.novadax.com/v1/market/ticker?symbol=BTC_BRL", timeout=10)
        response.raise_for_status()
        data = response.json()

        ask = data["data"]["ask"]
        bid = data["data"]["bid"]
        result = fill_exchange_info("nova_dax", ask, bid, 0.03)

        return result
    except Exception as e:
        print(f"Erro ao buscar Nova Dax: {e}")
        return None

def fetch_binance() -> dict | None:
    try: 
        response = requests.get("https://data-api.binance.vision/api/v3/ticker/bookTicker?symbol=BTCBRL", timeout=10)
        response.raise_for_status()
        data = response.json()

        ask = data["askPrice"]
        bid = data["bidPrice"]
        result = fill_exchange_info("binance", ask, bid, 0.1)

        return result
    except Exception as e:
        print(f"Erro ao buscar Binance: {e}")
        return None

def fetch_all_exchanges() -> list[dict] | None:
    raw_quotes  = [fetch_binance(), fetch_nova_dax(), fetch_mercado_bitcoin()]
    quotes = []

    for q in raw_quotes :
        if q is not None:
            quotes.append(q)

    return quotes