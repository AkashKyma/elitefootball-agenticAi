"use client";
import { useState } from "react";
import { TierBadge, TrajectoryBadge, ScoreBar, EmptyState, Card, Spinner } from "@/components/ui";
import Link from "next/link";

export default function ComparePage() {
  const [query, setQuery] = useState("");
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function search(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/compare?player_name=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error((await res.json()).detail || "Player not found");
      setData(await res.json());
    } catch (err: any) {
      setError(err.message);
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  const features = data?.comparison_features || {};
  const featureKeys = Object.keys(features);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Player Comparison</h1>
        <p className="text-slate-400 text-sm mt-1">Role-aware similarity engine with trajectory matching</p>
      </div>

      <form onSubmit={search} className="flex gap-3">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter player name..."
          className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
        />
        <button type="submit" disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-6 py-2.5 rounded-xl text-sm font-medium transition-colors">
          {loading ? "Searching..." : "Find Comps"}
        </button>
      </form>

      {error && <div className="bg-red-900/30 border border-red-700/50 text-red-300 rounded-xl p-4 text-sm">{error}</div>}
      {loading && <Spinner />}

      {data && (
        <div className="space-y-6">
          {/* Player header */}
          <Card>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-blue-600/20 border border-blue-600/30 rounded-full flex items-center justify-center text-blue-400 font-bold">
                {data.player_name?.[0]?.toUpperCase()}
              </div>
              <div>
                <h2 className="font-bold text-white">{data.player_name}</h2>
                <p className="text-slate-400 text-sm">{data.position} · Role: <span className="capitalize text-slate-300">{data.role}</span></p>
              </div>
            </div>
            {featureKeys.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs text-slate-400 uppercase tracking-wide mb-3">Feature Vector</p>
                {featureKeys.map((key) => (
                  <div key={key}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-400 capitalize">{key.replace(/_/g, " ")}</span>
                      <span className="text-slate-200">{Number(features[key]).toFixed(3)}</span>
                    </div>
                    <ScoreBar value={Number(features[key]) * 100} color="#3b82f6" />
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Comps */}
          <div>
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-3">
              {data.similar_players?.length} Similar Players
            </h3>
            <div className="space-y-2">
              {(data.similar_players || []).map((sim: any, i: number) => (
                <Link key={i} href={`/players/${encodeURIComponent(sim.player_name)}`}
                  className="bg-slate-800 border border-slate-700 hover:border-blue-600/50 rounded-xl p-4 flex items-center gap-4 transition-all group">
                  <span className="text-slate-500 text-sm w-5">{i + 1}.</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-white group-hover:text-blue-400 transition-colors">{sim.player_name}</span>
                      <TierBadge tier={sim.valuation_score >= 65 ? "high" : sim.valuation_score >= 50 ? "mid" : "developing"} />
                      {sim.trajectory && <TrajectoryBadge trajectory={sim.trajectory} />}
                    </div>
                    <p className="text-slate-400 text-xs mt-0.5">{sim.position} · {sim.current_club}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-slate-400 mb-1">Similarity</p>
                    <p className="text-blue-400 font-bold text-lg">{((sim.similarity_score || 0) * 100).toFixed(1)}%</p>
                  </div>
                  <div>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      sim.comp_classification === "successful" ? "bg-emerald-900/40 text-emerald-300" :
                      sim.comp_classification === "failed" ? "bg-red-900/40 text-red-300" :
                      "bg-slate-700 text-slate-400"
                    }`}>{sim.comp_classification || "neutral"}</span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}

      {!data && !loading && !error && (
        <EmptyState message="Enter a player name to find their most similar comparables." />
      )}
    </div>
  );
}
