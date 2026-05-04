import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from connection import engine
from models import BtcPrice, Indicator, FearGreed
from sqlalchemy.orm import Session

APORTE_MENSAL = 500

def carregar_dados():
    with Session(engine) as session:
        precos = session.query(BtcPrice).order_by(BtcPrice.date).all()
        indicadores = session.query(Indicator).order_by(Indicator.date).all()
        fear = session.query(FearGreed).order_by(FearGreed.date).all()

    preco_dict = {p.date: p.close for p in precos}
    ind_dict = {i.date: i.mayer_multiple for i in indicadores}
    fear_dict = {f.date: f.value for f in fear}

    return preco_dict, ind_dict, fear_dict

preco_dict, ind_dict, fear_dict = carregar_dados()
print(f"Dados carregados: {len(preco_dict)} preços")

def simular(preco_dict, ind_dict, fear_dict, mayer_limite, fear_limite, ate_ano=2022):
    btc_acumulado = 0
    total_investido = 0
    ultimo_mes = None
    saldo_acumulado = 0

    for data, preco in sorted(preco_dict.items()):
        if data.year > ate_ano:
            break

        mes_atual = (data.year, data.month)
        if mes_atual == ultimo_mes:
            continue

        saldo_acumulado += APORTE_MENSAL
        ultimo_mes = mes_atual

        mayer = ind_dict.get(data)
        fg = fear_dict.get(data)

        if mayer is None or fg is None:
            continue

        if mayer < mayer_limite and fg < fear_limite:
            btc_acumulado += saldo_acumulado / preco
            total_investido += saldo_acumulado
            saldo_acumulado = 0

    if total_investido == 0:
        return 0

    preco_final = sorted(p for d, p in preco_dict.items() if d.year <= ate_ano)[-1]
    valor_final = btc_acumulado * preco_final
    return ((valor_final - total_investido) / total_investido) * 100

print(simular(preco_dict, ind_dict, fear_dict, mayer_limite=1.2, fear_limite=40))

melhor_retorno = 0
melhor_mayer = 0
melhor_fear = 0

for mayer in [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]:
    for fear in [20, 25, 30, 35, 40, 45, 50]:
        retorno = simular(preco_dict, ind_dict, fear_dict, mayer, fear)
        if retorno > melhor_retorno:
            melhor_retorno = retorno
            melhor_mayer = mayer
            melhor_fear = fear

print(f"Melhor Mayer: {melhor_mayer}")
print(f"Melhor Fear & Greed: {melhor_fear}")
print(f"Melhor retorno (treino): {melhor_retorno:.1f}%")

retorno_teste = simular(preco_dict, ind_dict, fear_dict, melhor_mayer, melhor_fear, ate_ano=2026)
retorno_original = simular(preco_dict, ind_dict, fear_dict, 1.2, 40, ate_ano=2026)

print(f"\n=== Resultado no período de teste (2023+) ===")
print(f"Parâmetros otimizados (Mayer<{melhor_mayer}, Fear<{melhor_fear}): {retorno_teste:.1f}%")
print(f"Parâmetros originais  (Mayer<1.2, Fear<40): {retorno_original:.1f}%")