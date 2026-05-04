import React from 'react';

interface Strategy {
  total_investido: number;
  btc_acumulado: number;
  valor_final: number;
  retorno_pct: number;
  aportes_realizados?: number;
}

interface Backtest {
  dca_puro: Strategy;
  regras: Strategy;
}

interface Props {
  backtest: Backtest | null;
}

function formatUSD(value: number) {
  return value.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
}

export default function BacktestPanel({ backtest }: Props) {
  if (!backtest) return <div className="loading">Carregando backtest...</div>;

  return (
    <div>
      <p className="section-title">Backtest — Comparativo de Estratégias ($500/mês)</p>
      <div className="backtest-grid">
        <div className="backtest-card">
          <div className="backtest-card-title">
            DCA Puro <span>Aporte mensal fixo</span>
          </div>
          <div>
            <div className="backtest-metric">
              <span className="backtest-metric-label">Total investido</span>
              <span className="backtest-metric-value">{formatUSD(backtest.dca_puro.total_investido)}</span>
            </div>
            <div className="backtest-metric">
              <span className="backtest-metric-label">BTC acumulado</span>
              <span className="backtest-metric-value orange">{backtest.dca_puro.btc_acumulado.toFixed(4)} BTC</span>
            </div>
            <div className="backtest-metric">
              <span className="backtest-metric-label">Valor final</span>
              <span className="backtest-metric-value">{formatUSD(backtest.dca_puro.valor_final)}</span>
            </div>
            <div className="backtest-metric">
              <span className="backtest-metric-label">Retorno total</span>
              <span className="backtest-metric-value positive">+{backtest.dca_puro.retorno_pct.toLocaleString('pt-BR')}%</span>
            </div>
          </div>
        </div>

        <div className="backtest-card">
          <div className="backtest-card-title">
            Regras (Mayer + Fear & Greed) <span>Acumula e compra no pânico</span>
          </div>
          <div>
            <div className="backtest-metric">
              <span className="backtest-metric-label">Total investido</span>
              <span className="backtest-metric-value">{formatUSD(backtest.regras.total_investido)}</span>
            </div>
            <div className="backtest-metric">
              <span className="backtest-metric-label">BTC acumulado</span>
              <span className="backtest-metric-value orange">{backtest.regras.btc_acumulado.toFixed(4)} BTC</span>
            </div>
            <div className="backtest-metric">
              <span className="backtest-metric-label">Valor final</span>
              <span className="backtest-metric-value">{formatUSD(backtest.regras.valor_final)}</span>
            </div>
            <div className="backtest-metric">
              <span className="backtest-metric-label">Retorno total</span>
              <span className="backtest-metric-value positive">+{backtest.regras.retorno_pct.toLocaleString('pt-BR')}%</span>
            </div>
            {backtest.regras.aportes_realizados && (
              <div className="backtest-metric">
                <span className="backtest-metric-label">Aportes realizados</span>
                <span className="backtest-metric-value">{backtest.regras.aportes_realizados}x</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
