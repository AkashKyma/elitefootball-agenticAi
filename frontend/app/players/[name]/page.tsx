import { api } from "@/lib/api";
import { Card, TierBadge, TrajectoryBadge, ScoreBar, StatCard } from "@/components/ui";
import Link from "next/link";

function fmt(v: any) { return v !== null && v !== undefined ? String(v) : "—"; }
function fmtNum(v: any, d = 1) { return v !== null && v !== undefined ? Number(v).toFixed(d) : "—"; }

export default async function PlayerDetailPage({ params }: { params: Promise<{ name: string }> }) {
  const { name } = await params;
  const playerName = decodeURIComponent(name);

  const [players, stats, valuation, pathway, compare, advMetrics] = await Promise.allSettled([
    api.players({ name: playerName, limit: 1 }),
    api.playerStats(playerName),
    api.playerValuation(playerName),
    api.pathway(playerName),
    api.compare(playerName),
    api.advancedMetrics(playerName),
  ]);

  const player = players.status === "fulfilled" ? players.value.items[0] : null;
  const statsData = stats.status === "fulfilled" ? stats.value : null;
  const val = valuation.status === "fulfilled" ? valuation.value as any : null;
  const path = pathway.status === "fulfilled" ? pathway.value as any : null;
  const comp = compare.status === "fulfilled" ? compare.value : null;
  const adv = advMetrics.status === "fulfilled" ? advMetrics.value.items[0] : null;

  const kpi = player?.kpi;
  const features = player?.features;

  return (
    <div className="space-y-6">
      {/* Back */}
      <Link href="/players" className="text-slate-400 hover:text-white text-sm flex items-center gap-1 transition-colors">
        ← Back to Players
      </Link>

      {/* Player header */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 flex items-start gap-5">
        <div className="w-16 h-16 bg-blue-600/20 border border-blue-600/30 rounded-full flex items-center justify-center text-blue-400 font-bold text-2xl flex-shrink-0">
          {playerName[0]?.toUpperCase()}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-2xl font-bold text-white">{player?.preferred_name || playerName}</h1>
            {val && <TierBadge tier={val.valuation_tier} />}
            {path && <TrajectoryBadge trajectory={path.trajectory} />}
          </div>
          <p className="text-slate-400 mt-1">
            {player?.position || "—"} · {player?.current_club || "—"} · {player?.nationality || "—"}
          </p>
          {player?.date_of_birth && (
            <p className="text-slate-500 text-sm mt-0.5">DOB: {player.date_of_birth}</p>
          )}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Valuation */}
        {val && (
          <Card>
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-4">Valuation v2</h2>
            <div className="text-center mb-4">
              <div className="text-5xl font-bold text-blue-400">{val.valuation_score?.toFixed(1)}</div>
              <div className="text-slate-400 text-sm mt-1">/ 100</div>
              <TierBadge tier={val.valuation_tier} />
            </div>
            {val.components && (
              <div className="space-y-2 mt-4">
                {Object.entries(val.components).map(([key, v]: any) => (
                  <div key={key}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-400 capitalize">{key.replace(/_/g, " ")}</span>
                      <span className="text-slate-200 font-medium">{Number(v).toFixed(1)}</span>
                    </div>
                    <ScoreBar value={Number(v)} color="#3b82f6" />
                  </div>
                ))}
              </div>
            )}
            {val.future_value && (
              <div className="mt-4 pt-4 border-t border-slate-700">
                <p className="text-xs text-slate-400 mb-2 uppercase tracking-wide">Future Projection</p>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div><p className="text-xs text-slate-500">Now</p><p className="font-bold text-white">{val.future_value.current}</p></div>
                  <div><p className="text-xs text-slate-500">+2yr</p><p className="font-bold text-blue-400">{val.future_value.in_2yr}</p></div>
                  <div><p className="text-xs text-slate-500">+5yr</p><p className="font-bold text-purple-400">{val.future_value.in_5yr}</p></div>
                </div>
                <p className="text-xs text-slate-500 mt-2 text-center">Peak window: {val.future_value.peak_window}</p>
              </div>
            )}
          </Card>
        )}

        {/* Development Pathway */}
        {path && (
          <Card>
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-4">Development Pathway</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-400 text-sm">Stage</span>
                <span className="text-white text-sm font-medium capitalize">{path.development_stage || "—"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400 text-sm">Trajectory</span>
                <TrajectoryBadge trajectory={path.trajectory} />
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400 text-sm">Age Percentile</span>
                <span className="text-white text-sm font-medium">{fmtNum(path.age_league_percentile)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400 text-sm">Dev Velocity</span>
                <span className="text-emerald-400 text-sm font-medium">{fmtNum(path.development_velocity, 3)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400 text-sm">Success Prob</span>
                <span className="text-blue-400 text-sm font-bold">{((path.success_probability || 0) * 100).toFixed(1)}%</span>
              </div>
              {path.best_pathway && path.best_pathway.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-700">
                  <p className="text-xs text-slate-400 mb-2 uppercase tracking-wide">Recommended Next</p>
                  {path.best_pathway.map((p: string, i: number) => (
                    <div key={i} className="flex items-center gap-2 mb-1">
                      <span className="text-blue-400 text-xs">→</span>
                      <span className="text-slate-200 text-sm capitalize">{p}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>
        )}
      </div>

      {/* Advanced Metrics */}
      {adv && (
        <Card>
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-4">Advanced Metrics</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="xG Total" value={fmtNum(adv.xg_total, 2)} color="green" />
            <StatCard label="xA Total" value={fmtNum(adv.xa_total, 2)} color="blue" />
            <StatCard label="xG / 90" value={fmtNum(adv.xg_per_90, 3)} color="green" />
            <StatCard label="xA / 90" value={fmtNum(adv.xa_per_90, 3)} color="blue" />
            <StatCard label="xT / 90" value={fmtNum(adv.xt_per_90, 3)} color="purple" />
            <StatCard label="EPV / 90" value={fmtNum(adv.epv_per_90, 3)} color="yellow" />
            <StatCard label="OBV Total" value={fmtNum(adv.obv_total, 2)} color="purple" />
            <StatCard label="Progression" value={fmtNum(adv.progression_score, 2)} color="slate" />
          </div>
        </Card>
      )}

      {/* KPI */}
      {kpi && (
        <Card>
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-4">KPI Breakdown</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="KPI Score" value={fmtNum(kpi.base_kpi_score)} color="blue" />
            <StatCard label="Consistency" value={fmtNum(kpi.consistency_score, 3)} color="green" />
            <StatCard label="Age" value={fmtNum(kpi.age, 1)} color="slate" />
            <StatCard label="Minutes Played" value={fmt(kpi.minutes_played)} color="slate" />
          </div>
        </Card>
      )}

      {/* Match Stats */}
      {statsData && statsData.count > 0 && (
        <Card>
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-4">
            Recent Match Stats <span className="text-slate-500 normal-case font-normal">({statsData.count} matches)</span>
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  {["Date", "Club", "Mins", "G", "A", "Shots", "YC", "RC", "Source"].map((h) => (
                    <th key={h} className="text-left py-2.5 px-3 text-slate-400 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {statsData.items.slice(0, 15).map((row, i) => (
                  <tr key={i} className="border-b border-slate-800 hover:bg-slate-700/20 transition-colors">
                    <td className="py-2.5 px-3 text-slate-300">{row.match_date || "—"}</td>
                    <td className="py-2.5 px-3 text-slate-200">{row.club_name || "—"}</td>
                    <td className="py-2.5 px-3 text-slate-300">{row.minutes ?? "—"}</td>
                    <td className="py-2.5 px-3 text-emerald-400 font-medium">{row.goals ?? 0}</td>
                    <td className="py-2.5 px-3 text-blue-400 font-medium">{row.assists ?? 0}</td>
                    <td className="py-2.5 px-3 text-slate-300">{row.shots ?? 0}</td>
                    <td className="py-2.5 px-3 text-amber-400">{row.yellow_cards ?? 0}</td>
                    <td className="py-2.5 px-3 text-red-400">{row.red_cards ?? 0}</td>
                    <td className="py-2.5 px-3 text-slate-500 text-xs">{row.source || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Similar Players */}
      {comp && comp.similar_players.length > 0 && (
        <Card>
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-4">Similar Players</h2>
          <div className="space-y-2">
            {comp.similar_players.map((sim, i) => (
              <Link key={i} href={`/players/${encodeURIComponent(sim.player_name)}`}
                className="flex items-center justify-between py-2.5 px-3 rounded-lg hover:bg-slate-700/50 transition-colors group">
                <div className="flex items-center gap-3">
                  <span className="text-slate-500 text-sm w-5">{i + 1}.</span>
                  <div>
                    <span className="text-white text-sm font-medium group-hover:text-blue-400 transition-colors">{sim.player_name}</span>
                    <span className="text-slate-500 text-xs ml-2">{sim.position} · {sim.current_club}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {sim.comp_classification && (
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      sim.comp_classification === "successful" ? "bg-emerald-900/40 text-emerald-300" :
                      sim.comp_classification === "failed" ? "bg-red-900/40 text-red-300" :
                      "bg-slate-700 text-slate-400"
                    }`}>{sim.comp_classification}</span>
                  )}
                  <span className="text-blue-400 text-sm font-bold">{((sim.similarity_score || 0) * 100).toFixed(1)}%</span>
                </div>
              </Link>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
