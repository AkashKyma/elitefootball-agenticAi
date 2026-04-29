import { api } from "@/lib/api";
import { TierBadge, ScoreBar, EmptyState } from "@/components/ui";
import Link from "next/link";

export default async function ValuationPage({ searchParams }: { searchParams: Promise<{ tier?: string }> }) {
  const params = await searchParams;
  let rows: any[] = [];
  let total = 0;
  let error: string | null = null;

  try {
    const res = await api.valuation({ tier: params.tier, limit: 100 });
    rows = res.items;
    total = res.count;
  } catch (e: any) {
    error = e.message;
  }

  const tiers = ["elite", "high", "mid", "developing", "low"];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Player Valuation</h1>
        <p className="text-slate-400 text-sm mt-1">Weighted valuation model v2 · {total} players ranked</p>
      </div>

      {/* Tier filter */}
      <div className="flex gap-2 flex-wrap">
        <Link href="/valuation"
          className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${!params.tier ? "bg-blue-600 text-white" : "bg-slate-800 border border-slate-700 text-slate-400 hover:text-white"}`}>
          All
        </Link>
        {tiers.map((t) => (
          <Link key={t} href={`/valuation?tier=${t}`}
            className={`px-4 py-1.5 rounded-full text-sm font-medium capitalize transition-colors ${params.tier === t ? "bg-blue-600 text-white" : "bg-slate-800 border border-slate-700 text-slate-400 hover:text-white"}`}>
            {t}
          </Link>
        ))}
      </div>

      {error && <div className="bg-red-900/30 border border-red-700/50 text-red-300 rounded-xl p-4 text-sm">{error}</div>}
      {rows.length === 0 && !error && <EmptyState message="No valuation data. Run the pipeline first." />}

      <div className="space-y-2">
        {rows.map((row, i) => (
          <Link key={row.player_name} href={`/players/${encodeURIComponent(row.player_name)}`}
            className="bg-slate-800 border border-slate-700 hover:border-blue-600/50 rounded-xl p-4 flex items-center gap-4 transition-all group">
            <span className="text-slate-500 text-sm w-8 text-right flex-shrink-0">#{i + 1}</span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-semibold text-white group-hover:text-blue-400 transition-colors">{row.player_name}</span>
                <TierBadge tier={row.valuation_tier} />
              </div>
              <p className="text-slate-400 text-xs mt-0.5">{row.position || "—"} · {row.current_club || "—"} · {row.competition || "—"}</p>
            </div>
            <div className="w-32 flex-shrink-0">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-slate-400">Score</span>
                <span className="text-lg font-bold text-blue-400">{row.valuation_score?.toFixed(1)}</span>
              </div>
              <ScoreBar value={row.valuation_score || 0} color={
                row.valuation_tier === "elite" ? "#a78bfa" :
                row.valuation_tier === "high" ? "#34d399" :
                row.valuation_tier === "mid" ? "#fbbf24" : "#64748b"
              } />
            </div>
            {row.future_value && (
              <div className="text-right flex-shrink-0 hidden md:block">
                <p className="text-xs text-slate-500">+2yr / +5yr</p>
                <p className="text-sm font-medium">
                  <span className="text-blue-400">{row.future_value.in_2yr}</span>
                  <span className="text-slate-600 mx-1">/</span>
                  <span className="text-purple-400">{row.future_value.in_5yr}</span>
                </p>
              </div>
            )}
          </Link>
        ))}
      </div>

      {/* Model explanation */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-sm text-slate-400">
        <p className="font-medium text-slate-300 mb-2">Valuation Formula v2</p>
        <p className="font-mono text-xs">score = perf×0.35 + age_curve×0.20 + minutes×0.15 + league×0.15 + club_dev×0.10 − risk×0.05</p>
      </div>
    </div>
  );
}
