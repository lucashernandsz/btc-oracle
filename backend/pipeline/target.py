import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from connection import engine
from models import BtcPrice, Indicator, FearGreed, MlFeature
from sqlalchemy.orm import Session

def calcular_target():
    with Session(engine) as session:
        precos = session.query(BtcPrice).order_by(BtcPrice.date).all()
        indicadores = session.query(Indicator).order_by(Indicator.date).all()
        fear = session.query(FearGreed).order_by(FearGreed.date).all()

    df_price = pd.DataFrame([{"date": p.date, "close": p.close} for p in precos])
    df_ind = pd.DataFrame([{
        "date": i.date,
        "mayer_multiple": i.mayer_multiple,
        "rsi_14": i.rsi_14,
        "mm200": i.mm200,
        "variacao_7d": i.variacao_7d,
        "variacao_30d": i.variacao_30d
    } for i in indicadores])
    df_fear = pd.DataFrame([{"date": f.date, "fear_greed": f.value} for f in fear])

    df_price["preco_futuro_30d"] = df_price["close"].shift(-30)
    df_price["target"] = ((df_price["preco_futuro_30d"] - df_price["close"]) / df_price["close"] > 0.10).astype(int)

    df = df_ind.merge(df_fear, on="date", how="left")
    df = df.merge(df_price[["date", "target"]], on="date", how="left")
    df = df.dropna(subset=["target", "mayer_multiple"])

    with Session(engine) as session:
        count = 0
        for _, row in df.iterrows():
            exists = session.query(MlFeature).filter_by(date=row["date"]).first()
            if exists:
                continue

            record = MlFeature(
                date=row["date"],
                mayer_multiple=row["mayer_multiple"],
                rsi_14=row["rsi_14"],
                mm200=row["mm200"],
                variacao_7d=row["variacao_7d"],
                variacao_30d=row["variacao_30d"],
                fear_greed=row.get("fear_greed"),
                target=int(row["target"])
            )
            session.add(record)
            count += 1

        session.commit()
        print(f"{count} registros salvos em ml_features.")

calcular_target()
