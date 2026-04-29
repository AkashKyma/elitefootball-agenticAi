import { api } from "@/lib/api";
import { TierBadge, ScoreBar, EmptyState } from "@/components/ui";
import Link from "next/link";

export default async function PlayersPage({ searchParams }: { searchParams: Promise<{ name?: string; position?: string }> }) {
  const params = await searchParams;
  let players: any[] = [];
  let error: string | null = null;
  let total = 0;

  try {
    const res = await api.players({ name: params.name, position: params.position, limit: 50 });
    players = res.items;
    total = res.count;
  } catch (e: any) {
    error = e.message;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Players</h1>
          <p className="text-slate-400 text-sm mt-1">{total} players in system</p>
        </div>
      </div>

      {/* Search */}
      <form className="flex gap-3">
        <input
          name="name"
          defaultValue={params.name}
          placeholder="Search by name..."
          className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
        />
        <select
          name="position"
          defaultValue={params.position}
          className="bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
        >
          <option value="">All positions</option>
          <option value="Forward">Forward</option>
          <option value="Midfielder">Midfielder</option>
          <option value="Defender">Defender</option>
          <option value="Goalkeeper">Goalkeeper</option>
        </select>
        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl text-sm font-medium transition-colors">
          Search
        </button>
      </form>

      {error && <div className="bg-red-900/30 border border-red-700/50 text-red-300 rounded-xl p-4 text-sm">{error}</div>}

      {players.length === 0 && !error && <EmptyState message="No players found. Run the pipeline to populate data." />}

      <div className="grid gap-3">
        {players.map((player) => {
          const val = player.valuation;
          const kpi = player.kpi;
          return (
            <Link key={player.player_name} href={`/players/${encodeURIComponent(player.player_name)}`}
              className="bg-slate-800 border border-slate-700 hover:border-blue-600/50 rounded-xl p-4 flex items-center gap-4 transition-all group">
              <div className="w-10 h-10 bg-blue-600/20 border border-blue-600/30 rounded-full flex items-center justify-center text-blue-400 font-bold text-sm flex-shrink-0">
                {(player.player_name || "?")[0].toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-semibold text-white group-hover:text-blue-400 transition-colors">
                    {player.preferred_name || player.player_name}
                  </span>
                  {val && <TierBadge tier={val.valuation_tier} />}
                </div>
                <p className="text-slate-400 text-sm mt-0.5">
                  {player.position || "—"} · {player.current_club || "—"} · {player.nationality || "—"}
                </p>
              </div>
              <div className="text-right flex-shrink-0 hidden md:block">
                {val && (
                  <div className="w-24">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-slate-400">Value</span>
                      <span className="text-sm font-bold text-blue-400">{val.valuation_score?.toFixed(1)}</span>
                    </div>
                    <ScoreBar value={val.valuation_score || 0} color="#3b82f6" />
                  </div>
                )}
                {kpi && (
                  <div className="w-24 mt-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-slate-400">KPI</span>
                      <span className="text-sm font-bold text-emerald-400">{kpi.base_kpi_score?.toFixed(1)}</span>
                    </div>
                    <ScoreBar value={kpi.base_kpi_score || 0} color="#22c55e" />
                  </div>
                )}
              </div>
              <div className="text-slate-500 group-hover:text-slate-300 transition-colors">→</div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
