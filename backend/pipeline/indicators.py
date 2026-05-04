import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from connection import engine
from models import BtcPrice, Indicator
from sqlalchemy.orm import Session

def calcular_rsi(series, periodo=14):
    delta = series.diff()
    ganho = delta.where(delta > 0, 0).rolling(periodo).mean()
    perda = -delta.where(delta < 0, 0).rolling(periodo).mean()
    rs = ganho / perda
    return 100 - (100 / (1 + rs))

def calcular_indicadores():
    with Session(engine) as session:
        precos = session.query(BtcPrice).order_by(BtcPrice.date).all()

    df = pd.DataFrame([{
        "date": p.date,
        "close": p.close
    } for p in precos])

    df["mm200"] = df["close"].rolling(200).mean()
    df["mayer_multiple"] = df["close"] / df["mm200"]
    df["rsi_14"] = calcular_rsi(df["close"])
    df["variacao_7d"] = df["close"].pct_change(7) * 100
    df["variacao_30d"] = df["close"].pct_change(30) * 100

    with Session(engine) as session:
        count = 0
        for _, row in df.iterrows():
            if pd.isna(row["mm200"]):
                continue

            exists = session.query(Indicator).filter_by(date=row["date"]).first()
            if exists:
                continue

            record = Indicator(
                date=row["date"],
                mm200=row["mm200"],
                mayer_multiple=row["mayer_multiple"],
                rsi_14=row["rsi_14"],
                variacao_7d=row["variacao_7d"],
                variacao_30d=row["variacao_30d"]
            )
            session.add(record)
            count += 1

        session.commit()
        print(f"{count} indicadores salvos no banco.")

calcular_indicadores()
