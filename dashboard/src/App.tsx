import { useState } from 'react';
import type { DashboardMode, RiskMetric } from './types/federation';
import { MaritimeHeatmap } from './widgets/MaritimeHeatmap';
import { TradeFlowGraph } from './widgets/TradeFlowGraph';
import { InfrastructureStressMonitor } from './widgets/InfrastructureStressMonitor';
import { HealthcareLogisticsPanel } from './widgets/HealthcareLogisticsPanel';
import { ScenarioControls } from './widgets/ScenarioControls';

const syntheticRisks: RiskMetric[] = [
  { label: 'Port Alpha', value: 0.62, confidence: 0.74, rationale: 'Berth utilization and dwell time rising.' },
  { label: 'Port Beta', value: 0.31, confidence: 0.68, rationale: 'Weather disruption is low.' },
  { label: 'Port Gamma', value: 0.48, confidence: 0.71, rationale: 'Customs friction moderate.' },
];

export default function App() {
  const [mode, setMode] = useState<DashboardMode>('sovereign');
  const [lastScenario, setLastScenario] = useState<string>('No simulation run yet.');

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-slate-100">
      <header className="mb-6 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold">AetherOS Federated Dashboard</h1>
          <p className="text-sm text-slate-400">Advisory-only situational awareness with scoped visibility.</p>
        </div>
        <select className="rounded-lg bg-slate-800 p-2" value={mode} onChange={(event) => setMode(event.target.value as DashboardMode)}>
          <option value="sovereign">Sovereign view</option>
          <option value="coalition">Shared coalition view</option>
          <option value="emergency">Emergency response view</option>
          <option value="simulation-only">Simulation-only mode</option>
        </select>
      </header>
      <div className="grid gap-4 xl:grid-cols-2">
        <MaritimeHeatmap risks={syntheticRisks} />
        <TradeFlowGraph />
        <InfrastructureStressMonitor />
        <HealthcareLogisticsPanel />
        <ScenarioControls mode={mode} onRun={() => setLastScenario('Synthetic tabletop scenario queued for human review.')} />
        <section className="rounded-xl border border-slate-700 bg-slate-900 p-4 text-sm text-slate-300">{lastScenario}</section>
      </div>
    </main>
  );
}
