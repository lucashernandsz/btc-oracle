import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ingestion'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pipeline'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'strategy'))

from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from connection import engine
from models import BtcPrice, Indicator, FearGreed, Signal, ExchangeQuote
from sqlalchemy.orm import Session
from sqlalchemy import func

from btc_prices import fetch_btc_prices
from fear_greed import fetch_fear_greed
from indicators import calcular_indicadores
from rules import gerar_sinais
from exchange_prices import fetch_all_exchanges
from compare_exchanges import calc_comparacao

scheduler = AsyncIOScheduler(timezone='America/Sao_Paulo')

def executar_pipeline():
    btc = fetch_btc_prices()
    fg = fetch_fear_greed()
    if btc > 0 or fg > 0:
        calcular_indicadores()
        gerar_sinais()
    return btc, fg

def job_diario():
    print(f"[{datetime.now()}] Atualizando dados...")
    btc, fg = executar_pipeline()

    if btc == 0 or fg == 0:
        print("Dados incompletos. Agendando retries...")
        hoje = datetime.now()
        for hora in [8, 12, 20]:
            if datetime.now().hour < hora:
                scheduler.add_job(
                    job_retry,
                    trigger=CronTrigger(hour=hora, minute=0),
                    id=f"retry_{hora}",
                    replace_existing=True,
                    max_instances=1,
                )

def job_coletar_precos_corretoras():
    quotes = fetch_all_exchanges()

    with Session(engine) as session:
        for q in quotes:
            session.add(ExchangeQuote(
                exchange=q['exchange'],
                ask_brl=q['ask_brl'],
                bid_brl=q['bid_brl'],
                spread=q['spread'],
                spread_pct=q['spread_pct'],
                taker_fee_pct=q['taker_fee_pct'],
                datetime=q['datetime']
            ))
        session.commit()

def job_retry():
    print(f"[{datetime.now()}] Retry de atualização...")
    executar_pipeline()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(job_diario, CronTrigger(hour=0, minute=0), id="job_diario", replace_existing=True)
    scheduler.add_job(job_coletar_precos_corretoras, 'interval', minutes = 5, id='exchanges_price')
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

    return [{"data": str(s.date), "sinal": s.signal_rule} for s in sinais]

@app.get("/api/price/history")
def price_history(limit: int = 365):
    with Session(engine) as session:
        precos = session.query(BtcPrice).order_by(BtcPrice.date.desc()).limit(limit).all()

    return [{"data": str(p.date), "close": p.close} for p in reversed(precos)]

@app.get("/api/backtest")
def backtest():
    APORTE_MENSAL = 500

    with Session(engine) as session:
        precos = session.query(BtcPrice).order_by(BtcPrice.date).all()
        sinais = session.query(Signal).order_by(Signal.date).all()

    preco_dict = {p.date: p.close for p in precos}
    sinal_dict = {s.date: s.signal_rule for s in sinais}

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

    btc_regras = 0
    investido_regras = 0
    saldo = 0
    ultimo_mes = None
    aportes_regras = 0
    for data, preco in sorted(preco_dict.items()):
        mes = (data.year, data.month)
        if mes != ultimo_mes:
            saldo += APORTE_MENSAL
            ultimo_mes = mes
        sinal = sinal_dict.get(data)
        if sinal == "COMPRA FORTE" and saldo > 0:
            btc_regras += saldo / preco
            investido_regras += saldo
            aportes_regras += 1
            saldo = 0

    preco_final = sorted(preco_dict.items())[-1][1]
    total_aportado_regras = investido_regras + saldo

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
            "saldo_parado": round(saldo, 2),
            "btc_acumulado": round(btc_regras, 6),
            "valor_final": round(btc_regras * preco_final, 2),
            "retorno_pct": round(((btc_regras * preco_final - total_aportado_regras) / total_aportado_regras) * 100, 1) if total_aportado_regras > 0 else 0
        }
    }

@app.get("/api/compare")
def compare(brl : float):
    quotes = fetch_all_exchanges()
    return calc_comparacao(brl, quotes)
    
@app.get("/api/exchanges/history")
def exchange_history(hours: int):
    limit = datetime.now() - timedelta(hours=hours)
    with Session(engine) as session:
        history = session.query(ExchangeQuote).filter(ExchangeQuote.datetime >= limit).order_by(ExchangeQuote.datetime).all()
    
    return [
        {
            "exchange": h.exchange,
            "ask_brl": h.ask_brl,
            "bid_brl": h.bid_brl,
            "spread_pct": h.spread_pct,
            "taker_fee_pct": h.taker_fee_pct,
            "datetime": str(h.datetime)
        }
        for h in history
    ]
    
@app.get("/api/exchanges/ranking")
def exchange_ranking(brl:float, hours: int):
    limit = datetime.now() - timedelta(hours=hours)
    with Session(engine) as session:
        avg_ask_raw = (session.query(ExchangeQuote.exchange, func.avg(ExchangeQuote.ask_brl), func.avg(ExchangeQuote.taker_fee_pct))
        .filter(ExchangeQuote.datetime >= limit).group_by(ExchangeQuote.exchange).all())

    avg_ask = []
    for a in avg_ask_raw:
        avg_ask.append({"exchange": a[0], "ask_brl": a[1], "taker_fee_pct": a[2]})

    comparacao_ranking = calc_comparacao(brl, avg_ask)

    return comparacao_ranking

    
    


    