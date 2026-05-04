import yfinance as yf
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from datetime import date
from connection import engine
from models import BtcPrice
from sqlalchemy.orm import Session

def fetch_btc_prices():
    df = yf.download("BTC-USD", start="2014-09-17", progress=False)

    with Session(engine) as session:
        count = 0
        for day, row in df.iterrows():
            d = day.date()

            exists = session.query(BtcPrice).filter_by(date=d).first()
            if exists:
                continue

            record = BtcPrice(
                date=d,
                open=float(row["Open"].iloc[0]),
                high=float(row["High"].iloc[0]),
                low=float(row["Low"].iloc[0]),
                close=float(row["Close"].iloc[0]),
                volume=float(row["Volume"].iloc[0])
            )
            session.add(record)
            count += 1

        session.commit()
        print(f"{count} registros salvos no banco.")

fetch_btc_prices()
