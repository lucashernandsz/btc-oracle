import React from 'react';

interface Status {
  data: string;
  preco: number;
  mayer_multiple: number;
  fear_greed: number;
  fear_greed_classificacao: string;
  sinal: string;
}

interface Props {
  status: Status | null;
}

function SignalBadge({ sinal }: { sinal: string }) {
  const cls = sinal.replace(' ', '-');
  return (
    <div className={`signal-badge ${cls}`}>
      <div className="signal-dot" />
      {sinal}
    </div>
  );
}

export default function StatusCards({ status }: Props) {
  if (!status) return <div className="loading">Carregando dados...</div>;

  const preco = status.preco.toLocaleString('pt-BR', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });

  return (
    <div>
      <p className="section-title">Situação do Mercado</p>
      <div className="cards-grid">
        <div className="card">
          <span className="card-label">Preço Bitcoin</span>
          <span className="card-value orange">{preco}</span>
          <span className="card-sub">Fechamento — {status.data}</span>
        </div>

        <div className="card">
          <span className="card-label">Mayer Multiple</span>
          <span className="card-value">{status.mayer_multiple.toFixed(2)}</span>
          <span className="card-sub">{status.mayer_multiple < 1.0 ? 'Abaixo da MM200 — historicamente barato' : status.mayer_multiple > 2.4 ? 'Acima de 2.4 — zona de euforia' : 'Dentro da faixa neutra'}</span>
        </div>

        <div className="card">
          <span className="card-label">Fear & Greed</span>
          <span className="card-value">{status.fear_greed}</span>
          <span className="card-sub">{status.fear_greed_classificacao}</span>
        </div>

        <div className="card">
          <span className="card-label">Sinal do Dia</span>
          <SignalBadge sinal={status.sinal} />
          <span className="card-sub">Baseado em Mayer + Fear & Greed</span>
        </div>
      </div>
    </div>
  );
}
