import { api } from "@/lib/api";
import { TrajectoryBadge, ScoreBar, EmptyState, Card } from "@/components/ui";
import Link from "next/link";

export default async function PathwayPage() {
  let rows: any[] = [];
  let error: string | null = null;

  try {
    const res = await api.pathway() as any;
    rows = res.items || [];
  } catch (e: any) {
    error = e.message;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Development Pathways</h1>
        <p className="text-slate-400 text-sm mt-1">Career trajectory, improvement velocity, and best pathway recommendations</p>
      </div>

      {error && <div className="bg-red-900/30 border border-red-700/50 text-red-300 rounded-xl p-4 text-sm">{error}</div>}
      {rows.length === 0 && !error && <EmptyState message="No pathway data available. Run the pipeline first." />}

      <div className="grid gap-4">
        {rows.map((row) => (
          <Link key={row.player_name} href={`/players/${encodeURIComponent(row.player_name)}`}
            className="bg-slate-800 border border-slate-700 hover:border-blue-600/50 rounded-xl p-5 transition-all group block">
            <div className="flex items-start justify-between flex-wrap gap-3">
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-semibold text-white group-hover:text-blue-400 transition-colors">{row.player_name}</span>
                  <TrajectoryBadge trajectory={row.trajectory} />
                  <span className="bg-slate-700 text-slate-300 text-xs px-2 py-0.5 rounded-full capitalize">{row.development_stage}</span>
                </div>
                <p className="text-slate-400 text-sm mt-1">{row.position || "—"} · {row.current_club || "—"}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-400">Success Probability</p>
                <p className="text-2xl font-bold text-blue-400">{((row.success_probability || 0) * 100).toFixed(1)}%</p>
              </div>
            </div>

            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <p className="text-xs text-slate-500">Age Percentile</p>
                <p className="text-sm font-medium text-white">{row.age_league_percentile?.toFixed(1) ?? "—"}%</p>
                <ScoreBar value={row.age_league_percentile || 0} color="#3b82f6" />
              </div>
              <div>
                <p className="text-xs text-slate-500">Improvement Rate</p>
                <p className="text-sm font-medium text-emerald-400">{row.improvement_rate?.toFixed(3) ?? "—"}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Dev Velocity</p>
                <p className="text-sm font-medium text-purple-400">{row.development_velocity?.toFixed(3) ?? "—"}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Minutes Trend</p>
                <p className="text-sm font-medium capitalize text-white">{row.minutes_growth?.trend || "—"}</p>
              </div>
            </div>

            {row.best_pathway && row.best_pathway.length > 0 && (
              <div className="mt-3 flex items-center gap-2 flex-wrap">
                <span className="text-xs text-slate-400">Pathway:</span>
                {row.best_pathway.map((p: string, i: number) => (
                  <span key={i} className="bg-blue-900/30 border border-blue-700/40 text-blue-300 text-xs px-2 py-0.5 rounded-full capitalize">{p}</span>
                ))}
              </div>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
