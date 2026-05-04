import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from connection import engine
from models import MlFeature
from sqlalchemy.orm import Session

def carregar_dados():
    with Session(engine) as session:
        registros = session.query(MlFeature).order_by(MlFeature.date).all()

    df = pd.DataFrame([{
        "date": r.date,
        "mayer_multiple": r.mayer_multiple,
        "rsi_14": r.rsi_14,
        "variacao_7d": r.variacao_7d,
        "variacao_30d": r.variacao_30d,
        "fear_greed": r.fear_greed,
        "target": r.target
    } for r in registros])

    return df

df = carregar_dados()
df = df.dropna(subset=["fear_greed"])
print(f"Registros após limpeza: {len(df)}")
print(f"Período: de {df['date'].min()} até {df['date'].max()}")

FEATURES = ["mayer_multiple", "rsi_14", "variacao_7d", "variacao_30d", "fear_greed"]

treino = df[df["date"].apply(lambda d: d.year) <= 2022]
validacao = df[df["date"].apply(lambda d: d.year) == 2023]
teste = df[df["date"].apply(lambda d: d.year) >= 2024]

print(f"Treino: {len(treino)} registros")
print(f"Validação: {len(validacao)} registros")
print(f"Teste: {len(teste)} registros")

X_treino = treino[FEATURES]
y_treino = treino["target"]

X_val = validacao[FEATURES]
y_val = validacao["target"]

X_teste = teste[FEATURES]
y_teste = teste["target"]

print("X_treino shape:", X_treino.shape)
print("y_treino shape:", y_treino.shape)

from xgboost import XGBClassifier

modelo = XGBClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    random_state=42,
    scale_pos_weight=1
)
modelo.fit(X_treino, y_treino)

print("Modelo treinado!")

from sklearn.metrics import classification_report

print("=== Validação (2023) ===")
print(classification_report(y_val, modelo.predict(X_val)))

print("=== Teste (2024+) ===")
print(classification_report(y_teste, modelo.predict(X_teste)))

from sklearn.metrics import precision_score

probabilidades = modelo.predict_proba(X_teste)[:, 1]

for limiar in [0.5, 0.6, 0.7, 0.8]:
    predicoes = (probabilidades >= limiar).astype(int)
    precision = precision_score(y_teste, predicoes, zero_division=0)
    total_sinais = predicoes.sum()
    print(f"Limiar {limiar} → Precision: {precision:.2f} | Sinais emitidos: {total_sinais}")

import pickle

LIMIAR = 0.65

os.makedirs(os.path.join(os.path.dirname(__file__), "saved"), exist_ok=True)
caminho = os.path.join(os.path.dirname(__file__), "saved", "modelo.pkl")

with open(caminho, "wb") as f:
    pickle.dump((modelo, LIMIAR), f)

print(f"Modelo salvo em: {caminho}")