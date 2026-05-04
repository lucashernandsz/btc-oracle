import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from connection import engine
from models import BtcPrice, Indicator, FearGreed, Signal
from sqlalchemy.orm import Session

app = FastAPI()

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
def status():
    with Session(engine) as session:
        preco = session.query(BtcPrice).order_by(BtcPrice.date.desc()).first()
        indicador = session.query(Indicator).order_by(Indicator.date.desc()).first()
        fear = session.query(FearGreed).order_by(FearGreed.date.desc()).first()
        sinal = session.query(Signal).order_by(Signal.date.desc()).first()

    return {
        "data": str(preco.date),
        "preco": preco.close,
        "mayer_multiple": indicador.mayer_multiple,
        "fear_greed": fear.value,
        "fear_greed_classificacao": fear.classification,
        "sinal": sinal.signal_rule
    }

@app.get("/api/signal/history")
def signal_history(limit: int = 30):
    with Session(engine) as session:
        sinais = session.query(Signal).order_by(Signal.date.desc()).limit(limit).all()

    return [
        {
            "data": str(s.date),
            "sinal": s.signal_rule
        }
        for s in sinais
    ]

@app.get("/api/price/history")
def price_history(limit: int = 365):
    with Session(engine) as session:
        precos = session.query(BtcPrice).order_by(BtcPrice.date.desc()).limit(limit).all()

    return [
        {
            "data": str(p.date),
            "close": p.close
        }
        for p in reversed(precos)
    ]

@app.get("/api/backtest")
def backtest():
    APORTE_MENSAL = 500

    with Session(engine) as session:
        precos = session.query(BtcPrice).order_by(BtcPrice.date).all()
        sinais = session.query(Signal).order_by(Signal.date).all()

    preco_dict = {p.date: p.close for p in precos}
    sinal_dict = {s.date: s.signal_rule for s in sinais}

    # DCA Puro
    btc_dca = 0
    investido_dca = 0
    ultimo_mes = None
    for data, preco in sorted(preco_dict.items()):
        mes = (data.year, data.month)
        if mes == ultimo_mes:
            continue
        btc_dca += APORTE_MENSAL / preco
        investido_dca += APORTE_MENSAL
        ultimo_mes = mes

    # Regras com acúmulo
    btc_regras = 0
    investido_regras = 0
    saldo = 0
    ultimo_mes = None
    aportes_regras = 0
    for data, preco in sorted(preco_dict.items()):
        mes = (data.year, data.month)
        if mes == ultimo_mes:
            continue
        saldo += APORTE_MENSAL
        ultimo_mes = mes
        sinal = sinal_dict.get(data)
        if sinal == "COMPRA FORTE":
            btc_regras += saldo / preco
            investido_regras += saldo
            aportes_regras += 1
            saldo = 0

    preco_final = sorted(preco_dict.items())[-1][1]

    return {
        "dca_puro": {
            "total_investido": investido_dca,
            "btc_acumulado": round(btc_dca, 6),
            "valor_final": round(btc_dca * preco_final, 2),
            "retorno_pct": round(((btc_dca * preco_final - investido_dca) / investido_dca) * 100, 1)
        },
        "regras": {
            "aportes_realizados": aportes_regras,
            "total_investido": investido_regras,
            "btc_acumulado": round(btc_regras, 6),
            "valor_final": round(btc_regras * preco_final, 2),
            "retorno_pct": round(((btc_regras * preco_final - investido_regras) / investido_regras) * 100, 1)
        }
    }
