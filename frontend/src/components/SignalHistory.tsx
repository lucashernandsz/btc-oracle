import React from 'react';

interface SignalEntry {
  data: string;
  sinal: string;
}

interface Props {
  signals: SignalEntry[];
}

export default function SignalHistory({ signals }: Props) {
  if (!signals.length) return <div className="loading">Carregando sinais...</div>;

  return (
    <div>
      <p className="section-title">Histórico de Sinais — Últimos 30 dias</p>
      <div className="signal-table">
        <div className="signal-table-header">
          <span>Data</span>
          <span>Sinal</span>
        </div>
        {signals.map((s) => {
          const cls = s.sinal.replace(' ', '-');
          return (
            <div className="signal-row" key={s.data}>
              <span className="signal-date">{new Date(s.data).toLocaleDateString('pt-BR')}</span>
              <span className={`signal-pill ${cls}`}>
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'currentColor', display: 'inline-block' }} />
                {s.sinal}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
