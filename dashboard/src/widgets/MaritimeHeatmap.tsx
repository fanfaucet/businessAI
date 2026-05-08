import type { RiskMetric } from '../types/federation';

interface Props {
  risks: RiskMetric[];
}

export function MaritimeHeatmap({ risks }: Props) {
  return (
    <section className="rounded-xl border border-slate-700 bg-slate-900 p-4 text-slate-100">
      <h2 className="text-lg font-semibold">Maritime Heatmap</h2>
      <p className="text-sm text-slate-400">Probabilistic congestion and disruption indicators.</p>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        {risks.map((risk) => (
          <div key={risk.label} className="rounded-lg bg-slate-800 p-3">
            <div className="flex justify-between text-sm">
              <span>{risk.label}</span>
              <span>{Math.round(risk.value * 100)}%</span>
            </div>
            <div className="mt-2 h-2 rounded bg-slate-700">
              <div className="h-2 rounded bg-cyan-400" style={{ width: `${Math.round(risk.value * 100)}%` }} />
            </div>
            <p className="mt-2 text-xs text-slate-400">Confidence {Math.round(risk.confidence * 100)}% · {risk.rationale}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
