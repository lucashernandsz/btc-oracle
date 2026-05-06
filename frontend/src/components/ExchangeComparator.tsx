import React, { useState } from 'react';

const API = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const EXCHANGE_NAMES: Record<string, string> = {
  binance: 'Binance',
  mercado_bitcoin: 'Mercado Bitcoin',
  nova_dax: 'NovaDAX',
};

const MEDALS = ['🥇', '🥈', '🥉'];

interface CompareResult {
  exchange: string;
  btc_recebido: number;
  taker_fee_pct: number;
}

export default function ExchangeComparator() {
  const [brlAmount, setBrlAmount] = useState('');
  const [results, setResults] = useState<CompareResult[]>([]);
  const [loading, setLoading] = useState(false);

  async function compare() {
    const val = Number(brlAmount);
    if (!brlAmount || isNaN(val) || val <= 0) return;
    setLoading(true);
    try {
      const r = await fetch(`${API}/api/compare?brl=${val}`);
      if (r.ok) setResults(await r.json());
    } catch {}
    setLoading(false);
  }

  const satsDiff =
    results.length >= 2
      ? Math.round((results[0].btc_recebido - results[results.length - 1].btc_recebido) * 1e8)
      : 0;

  const savings =
    results.length >= 2
      ? Number(brlAmount) * (1 - results[results.length - 1].btc_recebido / results[0].btc_recebido)
      : 0;

  return (
    <div className="comparator-container">
      <p className="section-title">Comparador de Corretoras</p>

      <div className="comparator-input-row">
        <span className="comparator-currency">R$</span>
        <input
          className="comparator-input"
          type="number"
          placeholder="5000"
          value={brlAmount}
          onChange={e => setBrlAmount(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && compare()}
        />
        <button className="comparator-btn" onClick={compare} disabled={loading}>
          {loading ? '...' : 'Comparar'}
        </button>
      </div>

      {results.length === 0 && !loading && (
        <div className="comparator-placeholder">Digite um valor para comparar</div>
      )}

      {results.length > 0 && (
        <>
          <table className="comparator-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Corretora</th>
                <th>BTC Recebido</th>
                <th>Taxa</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r, i) => (
                <tr key={r.exchange} className={i === 0 ? 'comparator-row-best' : ''}>
                  <td className="comparator-medal">{MEDALS[i] ?? i + 1}</td>
                  <td className="comparator-exchange">{EXCHANGE_NAMES[r.exchange] ?? r.exchange}</td>
                  <td className="comparator-btc">{r.btc_recebido.toFixed(8)} BTC</td>
                  <td className="comparator-fee">{r.taker_fee_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>

          {savings > 0.01 && (
            <div className="comparator-savings">
              Economia de{' '}
              <strong>
                R${' '}
                {savings.toLocaleString('pt-BR', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </strong>{' '}
              e{' '}
              <strong className="comparator-sats">+{satsDiff.toLocaleString('pt-BR')} sats</strong>{' '}
              escolhendo a melhor opção
            </div>
          )}
        </>
      )}
    </div>
  );
}
