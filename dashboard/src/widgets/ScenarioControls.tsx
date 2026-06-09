interface Props {
  mode: string;
  onRun: () => void;
}

export function ScenarioControls({ mode, onRun }: Props) {
  return (
    <section className="rounded-xl border border-slate-700 bg-slate-900 p-4 text-slate-100">
      <h2 className="text-lg font-semibold">Scenario Simulation</h2>
      <p className="text-sm text-slate-400">Current mode: {mode}. Outputs remain simulation-only until reviewed.</p>
      <button className="mt-4 rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950" onClick={onRun}>
        Run tabletop scenario
      </button>
    </section>
  );
}
