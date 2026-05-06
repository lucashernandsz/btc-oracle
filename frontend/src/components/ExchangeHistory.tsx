import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from 'recharts';

const API = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const EXCHANGE_COLORS: Record<string, string> = {
  binance: '#f7931a',
  mercado_bitcoin: '#58a6ff',
  nova_dax: '#3fb950',
};

const EXCHANGE_NAMES: Record<string, string> = {
  binance: 'Binance',
  mercado_bitcoin: 'Mercado Bitcoin',
  nova_dax: 'NovaDAX',
};

interface HistoryEntry {
  exchange: string;
  ask_brl: number;
  datetime: string;
}

interface PivotedEntry {
  datetime: string;
  [key: string]: string | number;
}

function pivotData(data: HistoryEntry[]): PivotedEntry[] {
  const map = new Map<string, PivotedEntry>();
  for (const entry of data) {
    const key = entry.datetime.substring(0, 16);
    if (!map.has(key)) map.set(key, { datetime: key });
    map.get(key)![entry.exchange] = entry.ask_brl;
  }
  return Array.from(map.values()).sort((a, b) =>
    String(a.datetime).localeCompare(String(b.datetime))
  );
}

function formatTime(str: string) {
  const d = new Date(str.replace(' ', 'T'));
  return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function formatBRL(value: number) {
  return `R$ ${value.toLocaleString('pt-BR', { maximumFractionDigits: 0 })}`;
}

export default function ExchangeHistory() {
  const [hours, setHours] = useState<24 | 168>(24);
  const [data, setData] = useState<PivotedEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`${API}/api/exchanges/history?hours=${hours}`)
      .then(r => (r.ok ? r.json() : []))
      .then((raw: HistoryEntry[]) => {
        setData(pivotData(raw));
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [hours]);

  return (
    <div className="exchange-history-container">
      <div className="chart-header">
        <span className="chart-title">Preço Ask por Corretora</span>
        <div className="period-selector">
          <button
            className={`period-btn${hours === 24 ? ' active' : ''}`}
            onClick={() => setHours(24)}
          >
            24h
          </button>
          <button
            className={`period-btn${hours === 168 ? ' active' : ''}`}
            onClick={() => setHours(168)}
          >
            7d
          </button>
        </div>
      </div>

      {loading && <div className="loading">Carregando histórico...</div>}
      {!loading && data.length === 0 && (
        <div className="loading">Sem dados no período</div>
      )}
      {!loading && data.length > 0 && (
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={data} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#21262d" vertical={false} />
            <XAxis
              dataKey="datetime"
              tickFormatter={formatTime}
              tick={{ fill: '#8b949e', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tickFormatter={formatBRL}
              tick={{ fill: '#8b949e', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              width={95}
              domain={['auto', 'auto']}
            />
            <Tooltip
              contentStyle={{
                background: '#161b22',
                border: '1px solid #30363d',
                borderRadius: 8,
                fontSize: 13,
              }}
              labelStyle={{ color: '#8b949e' }}
              formatter={(value: any, name: any) => [
                formatBRL(Number(value)),
                EXCHANGE_NAMES[String(name)] ?? String(name),
              ]}
              labelFormatter={(label: any) => String(label)}
            />
            <Legend
              formatter={value => EXCHANGE_NAMES[value] ?? value}
              wrapperStyle={{ fontSize: 12, paddingTop: 12 }}
            />
            {Object.keys(EXCHANGE_COLORS).map(exchange => (
              <Line
                key={exchange}
                type="monotone"
                dataKey={exchange}
                stroke={EXCHANGE_COLORS[exchange]}
                strokeWidth={2}
                dot={false}
                connectNulls
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
