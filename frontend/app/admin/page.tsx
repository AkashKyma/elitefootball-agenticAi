"use client";
import { useState, useEffect } from "react";
import { Card, StatusDot, Spinner } from "@/components/ui";

export default function AdminPage() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [pipelineResult, setPipelineResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/admin/status").then((r) => r.json()).then(setStatus).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, []);

  async function runPipeline() {
    setRunning(true);
    setPipelineResult(null);
    try {
      const res = await fetch("/api/admin/pipeline/run", { method: "POST" });
      const data = await res.json();
      setPipelineResult(data);
      const statusRes = await fetch("/api/admin/status");
      setStatus(await statusRes.json());
    } catch (e: any) {
      setPipelineResult({ status: "error", message: e.message });
    } finally {
      setRunning(false);
    }
  }

  async function refreshStatus() {
    setLoading(true);
    try {
      const res = await fetch("/api/admin/status");
      setStatus(await res.json());
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Admin Panel</h1>
        <p className="text-slate-400 text-sm mt-1">Pipeline control, data validation, and system management</p>
      </div>

      {error && <div className="bg-red-900/30 border border-red-700/50 text-red-300 rounded-xl p-4 text-sm">{error}</div>}

      {/* Pipeline controls */}
      <Card>
        <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-4">Pipeline Control</h2>
        <div className="flex gap-3 flex-wrap">
          <button
            onClick={runPipeline}
            disabled={running}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-6 py-2.5 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
          >
            {running && <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />}
            {running ? "Running Pipeline..." : "▶ Run Full Pipeline"}
          </button>
          <button
            onClick={refreshStatus}
            disabled={loading}
            className="bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white px-6 py-2.5 rounded-xl text-sm font-medium transition-colors"
          >
            ↺ Refresh Status
          </button>
        </div>

        {pipelineResult && (
          <div className={`mt-4 p-4 rounded-xl text-sm ${pipelineResult.status === "ok" ? "bg-emerald-900/30 border border-emerald-700/50 text-emerald-300" : "bg-red-900/30 border border-red-700/50 text-red-300"}`}>
            <p className="font-semibold mb-2">{pipelineResult.status === "ok" ? "✓ Pipeline completed" : "✗ Pipeline failed"}</p>
            {pipelineResult.message && <p>{pipelineResult.message}</p>}
            {pipelineResult.stages && (
              <div className="mt-2 space-y-1">
                {Object.entries(pipelineResult.stages).map(([stage, count]: any) => (
                  <div key={stage} className="flex justify-between">
                    <span className="text-emerald-400/70 capitalize">{stage}</span>
                    <span>{typeof count === "number" ? `${count} rows` : count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Artifact status */}
      {loading && <Spinner />}
      {status?.artifacts && (
        <Card>
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-4">Artifact Status</h2>
          <div className="space-y-2">
            {Object.entries(status.artifacts).map(([name, art]: any) => (
              <div key={name} className="flex items-center justify-between py-2 border-b border-slate-700/50 last:border-0">
                <div className="flex items-center gap-2">
                  <StatusDot status={art.exists ? "ready" : "missing"} />
                  <span className="text-slate-200 text-sm font-medium capitalize">{name.replace(/_/g, " ")}</span>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full ${art.exists ? "bg-emerald-900/30 text-emerald-400" : "bg-red-900/30 text-red-400"}`}>
                  {art.exists ? "exists" : "missing"}
                </span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Dashboard status */}
      {status?.dashboard && (
        <Card>
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-4">Dashboard Status</h2>
          <div className="flex items-center gap-2 mb-3">
            <StatusDot status={status.dashboard.status} />
            <span className="text-white font-medium capitalize">{status.dashboard.status}</span>
          </div>
          {status.dashboard.diagnostics?.recommended_action && (
            <p className="text-slate-400 text-sm">💡 {status.dashboard.diagnostics.recommended_action}</p>
          )}
          {status.dashboard.sync?.last_successful_sync_at && (
            <p className="text-slate-500 text-xs mt-2">Last sync: {new Date(status.dashboard.sync.last_successful_sync_at).toLocaleString()}</p>
          )}
        </Card>
      )}

      {/* System info */}
      <Card>
        <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-4">System Information</h2>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between"><span className="text-slate-400">API URL</span><span className="text-white font-mono text-xs">http://127.0.0.1:9001</span></div>
          <div className="flex justify-between"><span className="text-slate-400">Frontend Port</span><span className="text-white font-mono text-xs">3000</span></div>
          <div className="flex justify-between"><span className="text-slate-400">Pipeline</span><span className="text-white text-xs">Bronze → Silver → Gold</span></div>
          <div className="flex justify-between"><span className="text-slate-400">Valuation Model</span><span className="text-white text-xs">v2 Weighted</span></div>
          <div className="flex justify-between"><span className="text-slate-400">Similarity</span><span className="text-white text-xs">v2 Role-Aware</span></div>
        </div>
      </Card>
    </div>
  );
}
