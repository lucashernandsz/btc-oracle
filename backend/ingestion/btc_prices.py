import yfinance as yf
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from connection import engine
from models import BtcPrice
from sqlalchemy.dialects.postgresql import insert

def fetch_btc_prices() -> int:
    try:
        df = yf.download("BTC-USD", start="2014-09-17", progress=False)
        if df.empty:
            return 0

        rows = [
            {
                "date": day.date(),
                "open": float(row["Open"].iloc[0]),
                "high": float(row["High"].iloc[0]),
                "low": float(row["Low"].iloc[0]),
                "close": float(row["Close"].iloc[0]),
                "volume": float(row["Volume"].iloc[0]),
            }
            for day, row in df.iterrows()
        ]

        with engine.begin() as conn:
            stmt = insert(BtcPrice).values(rows).on_conflict_do_nothing(index_elements=["date"])
            result = conn.execute(stmt)
            count = result.rowcount
            print(f"{count} registros de preço salvos.")
            return count
    except Exception as e:
        print(f"Erro ao buscar preços BTC: {e}")
        return 0

if __name__ == "__main__":
    fetch_btc_prices()
