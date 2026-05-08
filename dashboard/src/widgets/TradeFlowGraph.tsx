export function TradeFlowGraph() {
  return (
    <section className="rounded-xl border border-slate-700 bg-slate-900 p-4 text-slate-100">
      <h2 className="text-lg font-semibold">Trade Flow Graph</h2>
      <p className="text-sm text-slate-400">Shared constraint graph placeholder; edge weights represent advisory risk propagation.</p>
      <div className="mt-4 rounded-lg border border-dashed border-slate-600 p-6 text-center text-sm text-slate-400">
        Graph renderer integration point (e.g., Cytoscape/D3) — no external API assumed.
      </div>
    </section>
  );
}
