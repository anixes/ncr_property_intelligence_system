import React from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import { TrendingUp, Percent, ArrowUpRight, ArrowDownRight, Layers } from 'lucide-react';

const DATA = [
  { month: 'OCT', gurgaon: 4.2, noida: 3.8, grNoida: 3.5 },
  { month: 'NOV', gurgaon: 4.5, noida: 4.0, grNoida: 3.7 },
  { month: 'DEC', gurgaon: 4.8, noida: 4.1, grNoida: 3.8 },
  { month: 'JAN', gurgaon: 5.1, noida: 4.3, grNoida: 4.0 },
  { month: 'FEB', gurgaon: 5.4, noida: 4.5, grNoida: 4.2 },
  { month: 'MAR', gurgaon: 5.8, noida: 4.8, grNoida: 4.5 },
];

const YIELD_DATA = [
  { region: 'Gurgaon', yield: 5.8, color: '#8B5CF6' },
  { region: 'Noida', yield: 4.8, color: '#10B981' },
  { region: 'Gr. Noida', yield: 4.5, color: '#3B82F6' },
];

export default function RoiAnalyticsView() {
  return (
    <div className="space-y-8 h-full">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <RoiMetricCard 
          label="Aggregate NCR Yield" 
          val="5.03%" 
          delta="+0.4%" 
          positive={true} 
          icon={<Percent className="w-4 h-4" />} 
        />
        <RoiMetricCard 
          label="Gurgaon High-End Delta" 
          val="₹12.4k/sqft" 
          delta="+₹2.1k" 
          positive={true} 
          icon={<TrendingUp className="w-4 h-4" />} 
        />
        <RoiMetricCard 
          label="Market Absorption Rate" 
          val="84.2%" 
          delta="-2.1%" 
          positive={false} 
          icon={<Layers className="w-4 h-4" />} 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Yield Trending Chart */}
        <div className="lg:col-span-2 bg-[#1c1b1b] border border-white/5 rounded-2xl p-8 space-y-8">
          <div className="flex items-center justify-between">
            <h3 className="text-[12px] font-mono text-zinc-400 uppercase tracking-[0.3em]">Institutional Yield Trending (6M)</h3>
            <div className="flex items-center gap-4">
               <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-purple-500" /><span className="text-[9px] font-mono font-bold text-zinc-500 uppercase">GUR</span></div>
               <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-emerald-500" /><span className="text-[9px] font-mono font-bold text-zinc-500 uppercase">NOI</span></div>
               <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-blue-500" /><span className="text-[9px] font-mono font-bold text-zinc-500 uppercase">GRN</span></div>
            </div>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={DATA}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                <XAxis 
                  dataKey="month" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#3f3f46', fontSize: 10, fontWeight: 700 }} 
                />
                <YAxis 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#3f3f46', fontSize: 10, fontWeight: 700 }}
                  tickFormatter={(v) => `${v}%`}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#09090b', border: '1px solid #ffffff10', borderRadius: '12px', fontSize: '10px' }}
                  itemStyle={{ color: '#fff', fontSize: '10px' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="gurgaon" 
                  stroke="#8B5CF6" 
                  strokeWidth={3} 
                  dot={false} 
                  activeDot={{ r: 4, strokeWidth: 0 }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="noida" 
                  stroke="#10B981" 
                  strokeWidth={3} 
                  dot={false} 
                  activeDot={{ r: 4, strokeWidth: 0 }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="grNoida" 
                  stroke="#3B82F6" 
                  strokeWidth={3} 
                  dot={false} 
                  activeDot={{ r: 4, strokeWidth: 0 }} 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Current Spreads Column */}
        <div className="bg-[#1c1b1b] border border-white/5 rounded-2xl p-8 space-y-8">
          <h3 className="text-[12px] font-mono text-zinc-400 uppercase tracking-[0.3em]">Current Yield Spreads</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={YIELD_DATA} layout="vertical">
                <XAxis type="number" hide />
                <YAxis 
                  dataKey="region" 
                  type="category" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#fff', fontSize: 10, fontWeight: 900 }}
                  width={70}
                />
                <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ backgroundColor: '#09090b', border: '1px solid #ffffff10', fontSize: '10px' }} />
                <Bar dataKey="yield" radius={[0, 8, 8, 0]} barSize={24}>
                  {YIELD_DATA.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} fillOpacity={0.2} stroke={entry.color} strokeWidth={2} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="pt-4 border-t border-white/5">
            <p className="text-[10px] text-zinc-500 font-mono italic leading-relaxed text-center">
              "Yield Delta indicates +120bps spread in Gurgaon Commercial Hubs vs Residential NCR Index."
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function RoiMetricCard({ label, val, delta, positive, icon }: any) {
  return (
    <div className="bg-[#1c1b1b] border border-white/5 rounded-2xl p-6 relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-6 flex justify-end opacity-20 group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <div className="space-y-4">
        <p className="text-[9px] font-mono text-zinc-500 uppercase tracking-[0.4em]">{label}</p>
        <div className="flex items-end gap-3">
          <h4 className="text-3xl font-black text-white tracking-tighter">{val}</h4>
          <div className={`flex items-center gap-1 mb-1 ${positive ? 'text-emerald-400' : 'text-rose-400'}`}>
            <span className="text-[10px] font-mono font-black">{delta}</span>
            {positive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
          </div>
        </div>
      </div>
    </div>
  );
}
