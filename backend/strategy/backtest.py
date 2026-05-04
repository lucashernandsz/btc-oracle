import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from connection import engine
from models import BtcPrice, Signal
from sqlalchemy.orm import Session

APORTE_MENSAL = 500

def carregar_dados():
    with Session(engine) as session:
        precos = session.query(BtcPrice).order_by(BtcPrice.date).all()
        sinais = session.query(Signal).order_by(Signal.date).all()

    preco_dict = {p.date: p.close for p in precos}
    sinal_dict = {s.date: s.signal_rule for s in sinais}

    return preco_dict, sinal_dict

preco_dict, sinal_dict = carregar_dados()
print(f"Preços carregados: {len(preco_dict)}")
print(f"Sinais carregados: {len(sinal_dict)}")

def dca_puro(preco_dict):
    btc_acumulado = 0
    total_investido = 0
    ultimo_mes = None

    for data, preco in sorted(preco_dict.items()):
        mes_atual = (data.year, data.month)
        if mes_atual == ultimo_mes:
            continue

        btc_acumulado += APORTE_MENSAL / preco
        total_investido += APORTE_MENSAL
        ultimo_mes = mes_atual

    preco_final = sorted(preco_dict.items())[-1][1]
    valor_final = btc_acumulado * preco_final
    retorno = ((valor_final - total_investido) / total_investido) * 100

    print(f"=== DCA Puro ===")
    print(f"Total investido: R${total_investido:,.0f}")
    print(f"BTC acumulado: {btc_acumulado:.6f}")
    print(f"Valor final: R${valor_final:,.0f}")
    print(f"Retorno: {retorno:.1f}%")

def dca_regras(preco_dict, sinal_dict):
    btc_acumulado = 0
    total_investido = 0
    ultimo_mes = None
    aportes = 0
    saldo_acumulado = 0

    for data, preco in sorted(preco_dict.items()):
        mes_atual = (data.year, data.month)
        if mes_atual == ultimo_mes:
            continue

        saldo_acumulado += APORTE_MENSAL
        ultimo_mes = mes_atual

        sinal = sinal_dict.get(data)
        if sinal == "COMPRA FORTE":
            btc_acumulado += saldo_acumulado / preco
            total_investido += saldo_acumulado
            aportes += 1
            saldo_acumulado = 0

    preco_final = sorted(preco_dict.items())[-1][1]
    valor_final = btc_acumulado * preco_final
    retorno = ((valor_final - total_investido) / total_investido) * 100

    print(f"=== Regras com acúmulo ===")
    print(f"Aportes realizados: {aportes}")
    print(f"Total investido: R${total_investido:,.0f}")
    print(f"BTC acumulado: {btc_acumulado:.6f}")
    print(f"Valor final: R${valor_final:,.0f}")
    print(f"Retorno: {retorno:.1f}%")

dca_regras(preco_dict, sinal_dict)

dca_puro(preco_dict)