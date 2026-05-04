import React, { useEffect, useState } from 'react';
import './App.css';
import StatusCards from './components/StatusCards';
import PriceChart from './components/PriceChart';
import SignalHistory from './components/SignalHistory';
import BacktestPanel from './components/BacktestPanel';

const API = 'http://127.0.0.1:8000';

export default function App() {
  const [status, setStatus] = useState(null);
  const [prices, setPrices] = useState([]);
  const [signals, setSignals] = useState([]);
  const [backtest, setBacktest] = useState(null);

  useEffect(() => {
    const get = (url: string, setter: (d: any) => void) =>
      fetch(url).then(r => r.ok ? r.json() : null).then(d => d && setter(d)).catch(() => {});

    get(`${API}/api/status`, setStatus);
    get(`${API}/api/price/history?limit=365`, setPrices);
    get(`${API}/api/signal/history?limit=30`, setSignals);
    get(`${API}/api/backtest`, setBacktest);
  }, []);

  const today = new Date().toLocaleDateString('pt-BR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <h1>₿ BTC Oracle</h1>
          <span>Análise Quantitativa</span>
        </div>
        <span className="header-date">{today}</span>
      </header>

      <main className="main">
        <StatusCards status={status} />
        <PriceChart prices={prices} />
        <div className="two-col">
          <SignalHistory signals={signals} />
          <BacktestPanel backtest={backtest} />
        </div>
      </main>
    </div>
  );
}
