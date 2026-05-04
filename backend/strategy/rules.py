import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from connection import engine
from models import Indicator, FearGreed, Signal
from sqlalchemy.orm import Session

def aplicar_regras(mayer_multiple, fear_greed):
    if mayer_multiple < 0.9 and fear_greed < 20:
        return "COMPRA FORTE"
    elif mayer_multiple < 1.2 and fear_greed < 40:
        return "COMPRA"
    elif mayer_multiple > 2.4 or fear_greed > 80:
        return "EVITAR"
    else:
        return "NEUTRO"

def gerar_sinais():
    with Session(engine) as session:
        indicadores = session.query(Indicator).order_by(Indicator.date).all()
        fear = session.query(FearGreed).order_by(FearGreed.date).all()

    fear_dict = {f.date: f.value for f in fear}

    with Session(engine) as session:
        count = 0
        for ind in indicadores:
            fg = fear_dict.get(ind.date)
            if fg is None:
                continue

            recomendacao = aplicar_regras(ind.mayer_multiple, fg)

            exists = session.query(Signal).filter_by(date=ind.date).first()
            if exists:
                continue

            record = Signal(
                date=ind.date,
                signal_rule=recomendacao,
                recomendacao=recomendacao
            )
            session.add(record)
            count += 1

        session.commit()
        print(f"{count} sinais gerados.")

gerar_sinais()
