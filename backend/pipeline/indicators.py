import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from connection import engine
from models import BtcPrice, Indicator
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

def calcular_rsi(series, periodo=14):
    delta = series.diff()
    ganho = delta.where(delta > 0, 0).rolling(periodo).mean()
    perda = -delta.where(delta < 0, 0).rolling(periodo).mean()
    rs = ganho / perda
    return 100 - (100 / (1 + rs))

def calcular_indicadores() -> int:
    try:
        with Session(engine) as session:
            precos = session.query(BtcPrice).order_by(BtcPrice.date).all()

        df = pd.DataFrame([{"date": p.date, "close": p.close} for p in precos])
        df["mm200"] = df["close"].rolling(200).mean()
        df["mm20"] = df["close"].rolling(20).mean()
        df["mayer_multiple"] = df["close"] / df["mm200"]
        df["rsi_14"] = calcular_rsi(df["close"])
        df["variacao_7d"] = df["close"].pct_change(7) * 100
        df["variacao_30d"] = df["close"].pct_change(30) * 100

        rows = [
            {
                "date": row["date"],
                "mm200": row["mm200"],
                "mm20": row["mm20"],
                "mayer_multiple": row["mayer_multiple"],
                "rsi_14": row["rsi_14"],
                "variacao_7d": row["variacao_7d"],
                "variacao_30d": row["variacao_30d"],
            }
            for _, row in df.iterrows()
            if not pd.isna(row["mm200"])
        ]

        with engine.begin() as conn:
            stmt = insert(Indicator).values(rows).on_conflict_do_update(
                index_elements=["date"],
                set_={"mm200": insert(Indicator).excluded.mm200, "mm20": insert(Indicator).excluded.mm20, "mayer_multiple": insert(Indicator).excluded.mayer_multiple, "rsi_14": insert(Indicator).excluded.rsi_14, "variacao_7d": insert(Indicator).excluded.variacao_7d, "variacao_30d": insert(Indicator).excluded.variacao_30d}
            )
            result = conn.execute(stmt)
            count = result.rowcount
            print(f"{count} indicadores salvos.")
            return count
    except Exception as e:
        print(f"Erro ao calcular indicadores: {e}")
        return 0

if __name__ == "__main__":
    calcular_indicadores()
