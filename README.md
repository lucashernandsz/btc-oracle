# BTC Oracle

Um sistema de análise quantitativa do Bitcoin que construí para responder uma pergunta que me incomodava: **dá para usar dados históricos para saber se é um bom momento de comprar?**

Não é uma resposta definitiva. Mas é uma tentativa, com pipeline de dados real, backtesting e um dashboard para acompanhar os indicadores do dia.

---

## O que o sistema faz

Todo dia o sistema coleta os preços do Bitcoin e o índice de medo e ganância do mercado (Fear & Greed Index). Com esses dados, calcula indicadores financeiros clássicos e gera um sinal de recomendação: **COMPRA FORTE**, **COMPRA**, **NEUTRO** ou **EVITAR**.

O dashboard mostra tudo isso em tempo real — preço atual, indicadores do dia, histórico de sinais e comparação entre estratégias de investimento.

---

## Lógica de recomendação

O sistema usa dois indicadores consagrados no mercado de Bitcoin:

**Mayer Multiple** — divide o preço atual pela média móvel dos últimos 200 dias. Quando está abaixo de 1, o Bitcoin está sendo negociado abaixo da sua média histórica — historicamente um bom momento para comprar.

**Fear & Greed Index** — vai de 0 a 100 e mede o sentimento do mercado. Quanto mais perto de zero, maior o pânico. Dizem que o melhor momento de comprar é quando todos estão com medo.

```
COMPRA FORTE  →  Mayer < 0.9  E  Fear & Greed < 20
COMPRA        →  Mayer < 1.2  E  Fear & Greed < 40
NEUTRO        →  Mayer entre 1.2 e 2.4
EVITAR        →  Mayer > 2.4  OU  Fear & Greed > 80
```

Os limiares do **COMPRA FORTE** foram otimizados pelo backtesting: testei 49 combinações de parâmetros nos dados históricos até 2022 e validei nos dados de 2023 em diante.

---

## O que o backtesting mostrou

Simulei duas estratégias com aporte de R$500/mês desde 2018:

| Estratégia | Total investido | Valor final | Retorno |
|---|---|---|---|
| DCA Puro (todo mês) | R$70.500 | R$3.643.229 | +5.067% |
| Regras (acumula e compra no pânico) | R$70.000 | R$483.961 | +591% |

O DCA venceu. Para o Bitcoin, que tem tendência histórica de alta forte, ficar no mercado o tempo todo venceu tentar acertar o timing. As regras fazem mais sentido para quem não consegue aportar todo mês e prefere esperar momentos de pânico.

---

## O modelo de Machine Learning

Treinei um XGBoost para prever se o Bitcoin vai subir mais de 10% nos próximos 30 dias. O modelo aprendeu com dados de 2018 a 2022 e foi testado em 2023 em diante.

A precision ficou em torno de 25% — fraca. Mercado financeiro é difícil de prever e não faz sentido fingir que não é. O modelo está documentado no projeto exatamente assim: um experimento com resultado ruim, que ensina tanto quanto um com resultado bom.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Coleta de dados | Python + yfinance + Alternative.me API |
| Banco de dados | PostgreSQL + SQLAlchemy |
| Machine Learning | XGBoost + scikit-learn + pandas |
| API | FastAPI |
| Frontend | React + TypeScript + Recharts |
| Infraestrutura | Docker + docker-compose |

---

## Como rodar localmente

**Pré-requisitos:** Python 3.11+, Docker, Node.js

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/btc-oracle.git
cd btc-oracle

# Suba o banco de dados
docker-compose up -d

# Instale as dependências Python
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Popule o banco com dados históricos
cd backend/db && python create_tables.py
cd ../ingestion && python btc_prices.py && python fear_greed.py
cd ../pipeline && python indicators.py && python target.py
cd ../strategy && python rules.py

# Inicie a API
cd ../api && uvicorn main:app --reload

# Em outro terminal, inicie o frontend
cd frontend && npm install && npm start
```

Acesse `http://localhost:3000`.

---

## Estrutura do projeto

```
btc-oracle/
├── backend/
│   ├── ingestion/      # Coleta de dados (preços + Fear & Greed)
│   ├── db/             # Models, conexão, criação de tabelas
│   ├── pipeline/       # Cálculo de indicadores e targets para ML
│   ├── models/         # Treinamento do XGBoost
│   ├── strategy/       # Regras de recomendação e backtesting
│   └── api/            # FastAPI — endpoints para o frontend
├── frontend/           # React + TypeScript
├── sql/                # Queries analíticas
├── notebooks/          # Exploração e análise
└── docs/               # Documentação e planejamento
```

---

Projeto de portfólio cobrindo Engenharia de Dados, Data Science e Análise de Dados.
