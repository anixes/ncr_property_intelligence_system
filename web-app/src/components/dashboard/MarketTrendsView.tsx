import React from 'react';
import { motion } from 'framer-motion';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell 
} from 'recharts';
import { 
  Globe, TrendingUp, Users, MessageSquare, 
  ArrowUpRight, ArrowDownRight, Compass
} from 'lucide-react';

const SENTIMENT_DATA = [
  { category: 'Gurgaon', score: 82, trend: '+4%', dominant: 'Bullish' },
  { category: 'Noida', score: 68, trend: '+1%', dominant: 'Neutral' },
  { category: 'Greater Noida', score: 54, trend: '-2%', dominant: 'Caution' },
  { category: 'Commercial NCR', score: 71, trend: '+3%', dominant: 'Bullish' },
];

const VOLUME_DATA = [
  { day: 'MON', volume: 120, velocity: 85 },
  { day: 'TUE', volume: 150, velocity: 92 },
  { day: 'WED', volume: 180, velocity: 110 },
  { day: 'THU', volume: 220, velocity: 145 },
  { day: 'FRI', volume: 210, velocity: 130 },
  { day: 'SAT', volume: 140, velocity: 75 },
  { day: 'SUN', volume: 90, velocity: 40 },
];

export default function MarketTrendsView() {
  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      {/* Sentiment Overview Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {SENTIMENT_DATA.map((item, idx) => (
          <SentimentCard key={idx} {...item} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Market Velocity Chart */}
        <div className="bg-[#1c1b1b] border border-white/5 rounded-2xl p-8 space-y-8">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <h3 className="text-[12px] font-mono text-zinc-400 uppercase tracking-[0.3em]">Temporal Market Velocity</h3>
              <p className="text-[10px] text-zinc-600 font-mono">Volume vs Liquidity Speed (Real-time)</p>
            </div>
            <div className="flex gap-4">
               <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-purple-500" /><span className="text-[8px] font-mono text-zinc-500">VOLUME</span></div>
               <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-emerald-500" /><span className="text-[8px] font-mono text-zinc-500">VELOCITY</span></div>
            </div>
          </div>
          <div className="h-[300px]">
             <ResponsiveContainer width="100%" height="100%">
               <AreaChart data={VOLUME_DATA}>
                 <defs>
                   <linearGradient id="colorVol" x1="0" y1="0" x2="0" y2="1">
                     <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.1}/>
                     <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0}/>
                   </linearGradient>
                   <linearGradient id="colorVel" x1="0" y1="0" x2="0" y2="1">
                     <stop offset="5%" stopColor="#10B981" stopOpacity={0.1}/>
                     <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                   </linearGradient>
                 </defs>
                 <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                 <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{fill: '#3f3f46', fontSize: 10, fontWeight: 700}} />
                 <YAxis axisLine={false} tickLine={false} tick={{fill: '#3f3f46', fontSize: 10, fontWeight: 700}} />
                 <Tooltip contentStyle={{backgroundColor: '#09090b', border: '1px solid #ffffff10', fontSize: '10px'}} />
                 <Area type="monotone" dataKey="volume" stroke="#8B5CF6" fillOpacity={1} fill="url(#colorVol)" strokeWidth={3} />
                 <Area type="monotone" dataKey="velocity" stroke="#10B981" fillOpacity={1} fill="url(#colorVel)" strokeWidth={3} />
               </AreaChart>
             </ResponsiveContainer>
          </div>
        </div>

        {/* Global Signals Feed */}
        <div className="bg-[#1c1b1b] border border-white/5 rounded-2xl p-8 flex flex-col">
          <h3 className="text-[12px] font-mono text-zinc-400 uppercase tracking-[0.3em] mb-8">Alpha Signals Feed</h3>
          <div className="flex-1 space-y-6">
            <SignalItem 
              type="Bullish" 
              msg="Institutional pivot detected in Southern Peripheral Road. +12% volume surge."
              location="Gurgaon SPR"
              time="2m ago"
            />
            <SignalItem 
              type="Caution" 
              msg="Inventory overhang in Yamuna Expressway exceeding 18-month absorption."
              location="Greater Noida"
              time="15m ago"
            />
            <SignalItem 
              type="Bullish" 
              msg="Metro Link Phase 3 clearance triggers 400bps yield compression."
              location="Noida Sector 150"
              time="1h ago"
            />
            <SignalItem 
              type="Alpha" 
              msg="Under-valued land parcels identified in New Gurgaon expansion zone."
              location="Sector 80-95"
              time="3h ago"
            />
          </div>
          <button className="w-full mt-6 py-3 border border-white/5 rounded-xl text-[10px] font-mono text-zinc-500 uppercase tracking-widest hover:bg-white/5 transition-colors">
            View All Intelligence Logs
          </button>
        </div>
      </div>
    </div>
  );
}

function SentimentCard({ category, score, trend, dominant }: any) {
  const isPositive = trend.startsWith('+');
  return (
    <div className="bg-[#050505] border border-white/5 rounded-2xl p-6 space-y-4 hover:border-purple-500/20 transition-all group overflow-hidden relative">
      <div className="absolute -top-10 -right-10 w-24 h-24 bg-purple-500/5 blur-3xl group-hover:bg-purple-500/10 transition-all" />
      <div className="flex justify-between items-start">
        <p className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">{category}</p>
        <div className={`p-1 rounded-sm ${isPositive ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
          {isPositive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
        </div>
      </div>
      <div className="space-y-1">
        <h4 className="text-3xl font-black text-white tracking-tighter">{score}<span className="text-zinc-600">/100</span></h4>
        <div className="flex items-center gap-2">
          <span className="text-[9px] font-black uppercase text-zinc-400 tracking-widest">{dominant}</span>
          <span className={`text-[9px] font-mono ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>{trend}</span>
        </div>
      </div>
    </div>
  );
}

function SignalItem({ type, msg, location, time }: any) {
  const isAlpha = type === 'Alpha';
  return (
     <div className="flex gap-4 p-4 rounded-xl bg-white/[0.01] border border-white/[0.03] hover:bg-white/[0.03] transition-colors group">
       <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${isAlpha ? 'bg-amber-500/10 text-amber-500' : 'bg-purple-500/10 text-purple-400'}`}>
         {isAlpha ? <Compass className="w-5 h-5" /> : <MessageSquare className="w-5 h-5" />}
       </div>
       <div className="space-y-1">
         <div className="flex items-center gap-3">
           <span className="text-[9px] font-black uppercase text-white tracking-widest">{location}</span>
           <span className="text-[8px] font-mono text-zinc-600">{time}</span>
         </div>
         <p className="text-[11px] text-zinc-400 leading-relaxed font-medium group-hover:text-zinc-200 transition-colors">
           {msg}
         </p>
       </div>
     </div>
  );
}
