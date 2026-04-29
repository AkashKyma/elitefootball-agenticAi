"use client";
import React from "react";

export function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 ${className}`}>
      {children}
    </div>
  );
}

export function StatCard({ label, value, sub, color = "blue" }: { label: string; value: string | number; sub?: string; color?: string }) {
  const colors: Record<string, string> = {
    blue: "text-blue-400", green: "text-emerald-400", yellow: "text-amber-400",
    red: "text-red-400", purple: "text-purple-400", slate: "text-slate-400",
  };
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
      <p className="text-slate-400 text-sm mb-1">{label}</p>
      <p className={`text-2xl font-bold ${colors[color] || "text-white"}`}>{value}</p>
      {sub && <p className="text-slate-500 text-xs mt-1">{sub}</p>}
    </div>
  );
}

export function ScoreBar({ value, max = 100, color = "#3b82f6" }: { value: number; max?: number; color?: string }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  return (
    <div className="w-full bg-slate-700 rounded-full h-1.5 overflow-hidden">
      <div className="h-full rounded-full transition-all duration-500" style={{ width: `${pct}%`, background: color }} />
    </div>
  );
}

export function TierBadge({ tier }: { tier?: string }) {
  const cfg: Record<string, { label: string; cls: string }> = {
    elite: { label: "Elite", cls: "bg-purple-900/40 text-purple-300 border border-purple-700/50" },
    high: { label: "High", cls: "bg-emerald-900/40 text-emerald-300 border border-emerald-700/50" },
    mid: { label: "Mid", cls: "bg-amber-900/40 text-amber-300 border border-amber-700/50" },
    developing: { label: "Developing", cls: "bg-blue-900/40 text-blue-300 border border-blue-700/50" },
    low: { label: "Low", cls: "bg-slate-700/40 text-slate-400 border border-slate-600/50" },
  };
  const t = tier?.toLowerCase() || "low";
  const { label, cls } = cfg[t] || cfg.low;
  return <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold ${cls}`}>{label}</span>;
}

export function TrajectoryBadge({ trajectory }: { trajectory?: string }) {
  const cfg: Record<string, { label: string; cls: string; icon: string }> = {
    ascending: { label: "Ascending", cls: "bg-emerald-900/40 text-emerald-300 border border-emerald-700/50", icon: "↑" },
    stable: { label: "Stable", cls: "bg-blue-900/40 text-blue-300 border border-blue-700/50", icon: "→" },
    declining: { label: "Declining", cls: "bg-red-900/40 text-red-300 border border-red-700/50", icon: "↓" },
  };
  const t = trajectory?.toLowerCase() || "stable";
  const { label, cls, icon } = cfg[t] || cfg.stable;
  return <span className={`inline-flex gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${cls}`}>{icon} {label}</span>;
}

export function StatusDot({ status }: { status?: string }) {
  const colors: Record<string, string> = {
    ready: "bg-emerald-400", healthy: "bg-emerald-400",
    partial: "bg-amber-400", warning: "bg-amber-400",
    missing: "bg-red-400", error: "bg-red-400", artifact_missing: "bg-red-400",
    empty: "bg-slate-400",
  };
  const color = colors[status?.toLowerCase() || ""] || "bg-slate-400";
  return <span className={`inline-block w-2 h-2 rounded-full ${color}`} />;
}

export function Spinner() {
  return (
    <div className="flex justify-center items-center py-12">
      <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

export function ErrorAlert({ message }: { message: string }) {
  return (
    <div className="bg-red-900/30 border border-red-700/50 text-red-300 rounded-xl p-4 text-sm">
      {message}
    </div>
  );
}

export function EmptyState({ message = "No data available" }: { message?: string }) {
  return (
    <div className="text-center py-16 text-slate-500">
      <div className="text-4xl mb-3">⚽</div>
      <p>{message}</p>
    </div>
  );
}

export function Table({ headers, rows }: { headers: string[]; rows: (string | number | React.ReactNode)[][] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-700">
            {headers.map((h, i) => (
              <th key={i} className="text-left py-3 px-4 text-slate-400 font-medium">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-b border-slate-800 hover:bg-slate-700/30 transition-colors">
              {row.map((cell, j) => (
                <td key={j} className="py-3 px-4 text-slate-200">{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
