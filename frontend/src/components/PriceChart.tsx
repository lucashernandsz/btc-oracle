import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

interface PricePoint {
  data: string;
  close: number;
}

interface Props {
  prices: PricePoint[];
}

function formatPrice(value: number) {
  return `$${value.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('pt-BR', { month: 'short', year: '2-digit' });
}

export default function PriceChart({ prices }: Props) {
  if (!prices.length) return <div className="loading">Carregando gráfico...</div>;

  const latest = prices[prices.length - 1];

  return (
    <div className="chart-container">
      <div className="chart-header">
        <span className="chart-title">Histórico de Preço — Bitcoin (USD)</span>
        <span className="chart-price">{formatPrice(latest.close)}</span>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={prices} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="btcGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f7931a" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#f7931a" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262d" vertical={false} />
          <XAxis
            dataKey="data"
            tickFormatter={formatDate}
            tick={{ fill: '#8b949e', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            interval={Math.floor(prices.length / 6)}
          />
          <YAxis
            tickFormatter={formatPrice}
            tick={{ fill: '#8b949e', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={80}
          />
          <Tooltip
            contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, fontSize: 13 }}
            labelStyle={{ color: '#8b949e' }}
            itemStyle={{ color: '#f7931a' }}
            formatter={(value: any) => [formatPrice(Number(value)), 'Preço']}
            labelFormatter={(label) => new Date(label).toLocaleDateString('pt-BR')}
          />
          <Area
            type="monotone"
            dataKey="close"
            stroke="#f7931a"
            strokeWidth={2}
            fill="url(#btcGradient)"
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
