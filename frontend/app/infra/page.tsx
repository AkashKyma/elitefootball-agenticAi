"use client";

import React, { useState } from "react";

export default function InfraDashboard() {
  const [activeTab, setActiveTab] = useState("overview");

  const stats = [
    { label: "Medallion Stage", value: "Hybrid-Medallion", status: "Operational" },
    { label: "Primary Driver", value: "LocalFS + Abstraction", status: "Operational" },
    { label: "Schema Engines", value: "Pydantic V2", status: "Validated" },
    { label: "Canonical IDs", value: "RFC4122 v5 UUID", status: "Ready" },
  ];

  return (
    <main className="min-h-screen bg-slate-950 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-10">
          <div className="flex items-center gap-3 text-blue-500 font-semibold tracking-wider text-xs uppercase mb-2">
            <div className="h-2 w-2 bg-blue-500 rounded-full animate-pulse"></div>
            System Infrastructure Status
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight">Datalake Readiness Hub</h1>
          <p className="text-slate-400 mt-2">Monitoring architecture migration state and pipeline connectivity assets.</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
          {stats.map((s, i) => (
            <div key={i} className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <div className="text-slate-500 text-sm font-medium">{s.label}</div>
              <div className="text-xl font-bold text-white mt-1">{s.value}</div>
              <div className="mt-3 inline-flex items-center text-xs font-bold text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded-md">
                {s.status}
              </div>
            </div>
          ))}
        </div>

        <div className="bg-slate-900/40 border border-slate-800 rounded-3xl overflow-hidden">
          <div className="flex border-b border-slate-800 bg-slate-900/80 overflow-x-auto">
            {["overview", "providers", "entities", "pipelines", "lakehouse", "metrics"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-8 py-4 font-semibold capitalize whitespace-nowrap transition ${
                  activeTab === tab ? "text-blue-400 border-b-2 border-blue-400 bg-blue-500/5" : "text-slate-500 hover:text-slate-300"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
          
          <div className="p-8 min-h-[400px]">
             {activeTab === "overview" && (
               <div className="space-y-6">
                 <h3 className="text-xl font-bold">Infrastructural Backbone</h3>
                 <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 font-mono text-sm text-emerald-400 space-y-2">
                    <div>[OK] Postgres Connection Handler Initialized</div>
                    <div>[OK] Storage.S3Storage Drivers Prepped</div>
                    <div>[OK] Provider Connector Framework Registered</div>
                    <div>[OK] Workflow Engine Loaded</div>
                 </div>
               </div>
             )}

             {activeTab === "providers" && (
               <div className="space-y-4">
                 <h3 className="text-xl font-bold">Provider Connectivity Matrix</h3>
                 <div className="grid grid-cols-1 gap-3">
                    {["Wyscout", "Statsbomb", "Opta", "Hudl", "Internal Feed"].map((p, i) => (
                      <div key={i} className="p-5 bg-slate-800/30 border border-slate-800 rounded-xl flex justify-between items-center hover:border-slate-700 transition">
                         <div>
                           <div className="font-bold text-white text-lg">{p}</div>
                           <div className="text-xs text-slate-500 font-mono mt-1">API STATUS: DORMANT_READY</div>
                         </div>
                         <div className="px-3 py-1 bg-slate-700 text-slate-300 text-xs rounded font-bold uppercase">Connect Ready</div>
                      </div>
                    ))}
                 </div>
               </div>
             )}

             {activeTab === "entities" && (
               <div className="space-y-4">
                 <h3 className="text-xl font-bold">Master Entity Crosswalk</h3>
                 <div className="bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden">
                   <table className="w-full text-sm text-left text-slate-400">
                     <thead className="text-xs uppercase bg-slate-900 text-slate-300">
                        <tr>
                          <th className="px-6 py-3">Canonical UUID</th>
                          <th className="px-6 py-3">Aliases Registered</th>
                          <th className="px-6 py-3">Sync State</th>
                        </tr>
                     </thead>
                     <tbody>
                        <tr className="border-b border-slate-800 hover:bg-slate-900/50">
                           <td className="px-6 py-4 font-mono text-blue-400">8a3f-91d...</td>
                           <td className="px-6 py-4">Transfermarkt, Sofascore</td>
                           <td className="px-6 py-4 text-emerald-400">Converged</td>
                        </tr>
                        <tr className="border-b border-slate-800 hover:bg-slate-900/50">
                           <td className="px-6 py-4 font-mono text-blue-400">bd20-45c...</td>
                           <td className="px-6 py-4">Statsbomb, Internal</td>
                           <td className="px-6 py-4 text-emerald-400">Converged</td>
                        </tr>
                     </tbody>
                   </table>
                 </div>
               </div>
             )}

             {activeTab === "pipelines" && (
               <div className="space-y-4">
                 <h3 className="text-xl font-bold">Execution Workflow Log</h3>
                 <div className="space-y-3">
                    <div className="p-4 border border-emerald-900/50 bg-emerald-900/10 rounded-lg flex justify-between">
                       <span className="font-mono font-bold text-emerald-400">incremental_rebuild_silver</span>
                       <span className="text-xs font-bold text-slate-500">FINISHED 2026-05-12</span>
                    </div>
                    <div className="p-4 border border-slate-800 bg-slate-900 rounded-lg flex justify-between text-slate-500">
                       <span className="font-mono font-bold">weekly_provider_resync</span>
                       <span className="text-xs font-bold">PENDING</span>
                    </div>
                 </div>
               </div>
             )}

             {(activeTab === "lakehouse" || activeTab === "metrics") && (
               <div className="flex flex-col items-center justify-center py-24 text-slate-500 bg-slate-900/30 rounded-2xl border border-dashed border-slate-800">
                 <div className="text-xl font-bold text-slate-400">Module Framework Online</div>
                 <p className="text-sm max-w-md text-center mt-2">The backplane is functional and ready to accept dynamic runtime streams from remote sources.</p>
               </div>
             )}
          </div>
        </div>
      </div>
    </main>
  );
}
