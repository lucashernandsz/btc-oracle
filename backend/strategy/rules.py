import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from connection import engine
from models import BtcPrice, Indicator, FearGreed, Signal
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

def aplicar_regras(mayer_multiple, fear_greed, close, mm20):
    if mayer_multiple < 0.9 and fear_greed < 20:
        return "COMPRA FORTE"
    elif fear_greed < 50 and close < mm20:
        return "COMPRA"
    elif mayer_multiple < 1.2 and fear_greed < 40:
        return "COMPRA"
    elif mayer_multiple > 2.4 or fear_greed > 80:
        return "EVITAR"
    else:
        return "NEUTRO"

def gerar_sinais() -> int:
    try:
        with Session(engine) as session:
            indicadores = session.query(Indicator).order_by(Indicator.date).all()
            fear = session.query(FearGreed).order_by(FearGreed.date).all()
            precos = session.query(BtcPrice).order_by(BtcPrice.date).all()

        fear_dict = {f.date: f.value for f in fear}
        preco_dict = {p.date: p.close for p in precos}

        rows = [
            {
                "date": ind.date,
                "signal_rule": aplicar_regras(
                    ind.mayer_multiple,
                    fear_dict[ind.date],
                    preco_dict.get(ind.date, 0),
                    ind.mm20 or 0,
                ),
                "recomendacao": aplicar_regras(
                    ind.mayer_multiple,
                    fear_dict[ind.date],
                    preco_dict.get(ind.date, 0),
                    ind.mm20 or 0,
                ),
            }
            for ind in indicadores
            if ind.date in fear_dict
        ]

        with engine.begin() as conn:
            stmt = insert(Signal).values(rows).on_conflict_do_update(
                index_elements=["date"],
                set_={"signal_rule": insert(Signal).excluded.signal_rule, "recomendacao": insert(Signal).excluded.recomendacao}
            )
            result = conn.execute(stmt)
            count = result.rowcount
            print(f"{count} sinais gerados.")
            return count
    except Exception as e:
        print(f"Erro ao gerar sinais: {e}")
        return 0

if __name__ == "__main__":
    gerar_sinais()
