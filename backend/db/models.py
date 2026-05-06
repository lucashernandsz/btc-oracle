from sqlalchemy import Column, Date, Float, Integer, String, DateTime
from connection import Base


class BtcPrice(Base):
    __tablename__ = "btc_prices"

    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)


class FearGreed(Base):
    __tablename__ = "fear_greed"

    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, nullable=False)
    value = Column(Float)
    classification = Column(String)


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, nullable=False)
    mayer_multiple = Column(Float)
    rsi_14 = Column(Float)
    mm200 = Column(Float)
    mm20 = Column(Float)
    variacao_7d = Column(Float)
    variacao_30d = Column(Float)


class MlFeature(Base):
    __tablename__ = "ml_features"

    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, nullable=False)
    mayer_multiple = Column(Float)
    rsi_14 = Column(Float)
    mm200 = Column(Float)
    variacao_7d = Column(Float)
    variacao_30d = Column(Float)
    fear_greed = Column(Float)
    target = Column(Integer)


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, nullable=False)
    signal_rule = Column(String)
    signal_ml = Column(String)
    probabilidade = Column(Float)
    recomendacao = Column(String)


class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True)
    estrategia = Column(String)
    retorno_acumulado = Column(Float)
    sharpe = Column(Float)
    max_drawdown = Column(Float)

class ExchangeQuote(Base):
    __tablename__= "exchange_quote"

    id = Column(Integer, primary_key=True)
    exchange = Column(String(100), nullable = False)
    ask_brl = Column(Float, nullable = False)
    bid_brl = Column(Float, nullable = False)
    spread = Column(Float, nullable = False)
    spread_pct = Column(Float, nullable = False)
    taker_fee_pct = Column(Float, nullable = False)
    datetime = Column(DateTime, nullable = False)