import { api } from "@/lib/api";
import { ScoreBar, EmptyState } from "@/components/ui";

function MetricRow({ label, value, unit = "" }: { label: string; value?: number; unit?: string }) {
  if (value === undefined || value === null) return null;
  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-700/50 last:border-0">
      <span className="text-slate-400 text-sm">{label}</span>
      <span className="text-white text-sm font-semibold">{Number(value).toFixed(2)}{unit}</span>
    </div>
  );
}

export default async function BenchmarkPage() {
  let rows: any[] = [];
  let error: string | null = null;

  try {
    const res = await api.benchmark();
    rows = res.items;
  } catch (e: any) {
    error = e.message;
  }

  const colors: Record<string, string> = {
    IDV: "#3b82f6", Benfica: "#ef4444", Ajax: "#f59e0b", Salzburg: "#8b5cf6",
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Club Benchmarking</h1>
        <p className="text-slate-400 text-sm mt-1">IDV vs Benfica vs Ajax vs Salzburg — development quality comparison</p>
      </div>

      {error && <div className="bg-red-900/30 border border-red-700/50 text-red-300 rounded-xl p-4 text-sm">{error}</div>}
      {rows.length === 0 && !error && <EmptyState message="No benchmark data available." />}

      {/* Development score bar comparison */}
      {rows.length > 0 && (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-5">Development Score</h2>
          <div className="space-y-4">
            {rows.map((row) => (
              <div key={row.club}>
                <div className="flex justify-between mb-1.5">
                  <span className="text-white font-medium">{row.club}</span>
                  <span className="text-slate-300 font-bold">{row.development_score?.toFixed(1)}</span>
                </div>
                <ScoreBar value={row.development_score || 0} color={colors[row.club] || "#64748b"} />
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        {rows.map((row) => (
          <div key={row.club} className="bg-slate-800 border border-slate-700 rounded-xl p-5"
            style={{ borderTopColor: colors[row.club] || "#334155", borderTopWidth: 2 }}>
            <h3 className="font-bold text-white text-lg mb-4">{row.club}</h3>

            {row.reference_benchmarks && (
              <div className="mb-4">
                <p className="text-xs text-slate-400 uppercase tracking-wide mb-2">Reference Benchmarks</p>
                <MetricRow label="Player Improvement Rate" value={row.reference_benchmarks.avg_player_improvement_rate} />
                <MetricRow label="Resale Multiplier" value={row.reference_benchmarks.avg_resale_multiplier} unit="×" />
                <MetricRow label="Success Rate" value={row.reference_benchmarks.success_rate && row.reference_benchmarks.success_rate * 100} unit="%" />
                <MetricRow label="Avg Age at Breakout" value={row.reference_benchmarks.avg_age_at_breakout} />
                <MetricRow label="Players Exported to Europe" value={row.reference_benchmarks.players_exported_to_europe} />
              </div>
            )}

            {row.live_metrics?.live_data && (
              <div className="mt-3 pt-3 border-t border-slate-700">
                <p className="text-xs text-slate-400 uppercase tracking-wide mb-2">Live Data ({row.live_metrics.player_count} players)</p>
                <MetricRow label="Avg KPI Score" value={row.live_metrics.avg_kpi_score} />
                <MetricRow label="Avg Consistency" value={row.live_metrics.avg_consistency_score} />
              </div>
            )}

            {row.comparison_vs_idv && row.club !== "IDV" && (
              <div className="mt-3 pt-3 border-t border-slate-700">
                <p className="text-xs text-slate-400 uppercase tracking-wide mb-2">vs IDV</p>
                {Object.entries(row.comparison_vs_idv)
                  .filter(([k]) => k.includes("delta"))
                  .map(([k, v]: any) => (
                    <div key={k} className="flex justify-between py-1.5">
                      <span className="text-slate-400 text-xs capitalize">{k.replace(/_delta_vs_idv/, "").replace(/_/g, " ")}</span>
                      <span className={`text-xs font-semibold ${v > 0 ? "text-emerald-400" : "text-red-400"}`}>
                        {v > 0 ? "+" : ""}{Number(v).toFixed(2)}
                      </span>
                    </div>
                  ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
