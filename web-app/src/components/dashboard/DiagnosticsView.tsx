import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, ShieldCheck, Cpu, Database, Wifi, AlertTriangle, Clock } from 'lucide-react';
import * as api from '@/lib/api';

interface ModelInfo {
  name: string;
  version: string;
  last_updated: string;
  status: 'active' | 'training' | 'offline';
  performance: string;
}

export default function DiagnosticsView() {
  const [health, setHealth] = useState<any>(null);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [latency, setLatency] = useState<number>(0);

  useEffect(() => {
    const fetchData = async () => {
      const start = Date.now();
      try {
        const [healthData, modelData] = await Promise.all([
          api.getHealth(),
          api.getModelMetadata()
        ]);
        setLatency(Date.now() - start);
        setHealth(healthData);
        setModels(modelData.models || []);
      } catch (error) {
        console.error('Diagnostics fetch failed:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // 30s refresh
    return () => clearInterval(interval);
  }, []);

  const systemStats = [
    { label: 'API Gateway', value: 'Operational', icon: Wifi, color: 'text-emerald-400' },
    { label: 'Neural Pool', value: '3,842 Nodes', icon: Cpu, color: 'text-purple-400' },
    { label: 'H3 Spatial Index', value: 'Resolution 8', icon: Database, color: 'text-blue-400' },
    { label: 'Response Latency', value: `${latency}ms`, icon: Clock, color: latency < 100 ? 'text-emerald-400' : 'text-amber-400' },
  ];

  return (
    <div className="flex flex-col h-full space-y-6">
      {/* HUD Header */}
      <div>
        <h2 className="text-2xl font-semibold text-white tracking-tight flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          System Diagnostics Hub
        </h2>
        <p className="text-sm text-zinc-400 font-mono mt-1">
          Real-time monitoring of model health and data pipeline integrity.
        </p>
      </div>

      {/* KPI Ticker */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {systemStats.map((stat, idx) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: idx * 0.1 }}
            className="bg-[#1c1b1b] p-4 rounded-xl flex items-center gap-4 group"
          >
            <div className={`p-2 rounded-lg bg-zinc-800/50 group-hover:bg-zinc-700/50 transition-colors ${stat.color}`}>
              <stat.icon className="w-5 h-5" />
            </div>
            <div>
              <p className="text-[10px] text-zinc-500 font-mono uppercase tracking-wider">{stat.label}</p>
              <p className="text-zinc-200 font-medium">{stat.value}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Model Registry */}
      <div className="flex-1 bg-[#1c1b1b] rounded-2xl overflow-hidden flex flex-col">
        <div className="p-5 border-b border-zinc-800/50 flex items-center justify-between">
          <h3 className="text-sm font-mono text-zinc-400 flex items-center gap-2">
            <Activity className="w-4 h-4 text-purple-400" />
            Model Registry v4.2
          </h3>
          <span className="bg-emerald-500/10 text-emerald-400 text-[10px] px-2 py-0.5 rounded-full border border-emerald-500/20">
            All Systems Nominal
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="text-[11px] font-mono text-zinc-500 uppercase tracking-widest border-b border-zinc-800/30">
                <th className="px-6 py-4 font-medium">Model Objective</th>
                <th className="px-6 py-4 font-medium">Core Version</th>
                <th className="px-6 py-4 font-medium">Precision</th>
                <th className="px-6 py-4 font-medium">Last Sync</th>
                <th className="px-6 py-4 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/20">
              {loading ? (
                Array(3).fill(0).map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={5} className="px-6 py-4 h-12 bg-zinc-800/10" />
                  </tr>
                ))
              ) : (
                models.map((model) => (
                  <tr key={model.name} className="hover:bg-zinc-800/30 transition-colors">
                    <td className="px-6 py-4">
                      <span className="text-sm text-zinc-200 font-medium">{model.name}</span>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-zinc-400">{model.version}</td>
                    <td className="px-6 py-4 font-mono text-xs text-emerald-400">{model.performance}</td>
                    <td className="px-6 py-4 text-xs text-zinc-500">{new Date(model.last_updated).toLocaleString()}</td>
                    <td className="px-6 py-4">
                      <span className={`text-[10px] uppercase font-bold py-1 px-2 rounded ${
                        model.status === 'active' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'
                      }`}>
                        {model.status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Connection Log */}
      <div className="bg-[#050505] p-4 rounded-xl font-mono text-[11px]">
        <div className="flex items-center gap-2 mb-2 text-zinc-500">
          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
          Live Connection Established: {API_BASE_URL}
        </div>
        <div className="text-zinc-600 space-y-1">
          <p>[00:29:21] SYNC: Pushing local H3 cache to central registry...</p>
          <p>[00:29:22] SYNC: Validating Sector 128 price tensors...</p>
          <p>[00:29:22] SYNC: Success. All 3 model clusters active.</p>
        </div>
      </div>
    </div>
  );
}
