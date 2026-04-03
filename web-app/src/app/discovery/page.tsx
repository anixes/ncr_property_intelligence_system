'use client';

import React, { useState } from 'react';
import { discoverHotspots } from '@/lib/api';
import { DiscoveryResponse } from '@/types';
import { Loader2, ArrowUpRight, Radar } from 'lucide-react';

export default function Discovery() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DiscoveryResponse | null>(null);
  const [filters, setFilters] = useState({ city: 'Gurgaon', min_yield: 4.0 });

  const handleDiscover = async () => {
    setLoading(true);
    try {
      const data = await discoverHotspots(filters.city, filters.min_yield);
      setResult(data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20 lg:py-24 space-y-20 md:space-y-32">
      
      {/* HEADER SCANNER */}
      <header className="space-y-6 sm:space-y-8">
        <div className="inline-flex items-center gap-3 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-[10px] font-black uppercase tracking-[0.4em] border border-primary/10 font-body">
           Portfolio Scanners Active
        </div>
        <div className="space-y-4">
          <h1 className="text-4xl sm:text-5xl lg:text-7xl font-black font-headline tracking-tightest leading-[0.9] text-white">
             Discovery <br className="hidden sm:block"/>
             <span className="text-[#adaaab]">Void.</span>
          </h1>
          <p className="text-lg sm:text-xl md:text-2xl text-[#adaaab] font-light max-w-xl leading-relaxed tracking-tight font-body italic">
            Identify high-yield Alpha signals across the National Capital Region.
          </p>
        </div>
      </header>

      {/* FILTER PORTER */}
      <div className="bg-[#131314] rounded-[32px] sm:rounded-[40px] p-8 sm:p-10 flex flex-col lg:flex-row lg:items-end gap-10 sm:gap-12 shadow-2xl border border-white/5">
         
         <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-8 sm:gap-10">
            <div className="space-y-4">
               <span className="text-[10px] font-black uppercase tracking-[0.4em] text-primary font-body">Micro-Market Focus</span>
               <div className="relative">
                  <select 
                      value={filters.city} 
                      onChange={(e) => setFilters({...filters, city: e.target.value})} 
                      className="w-full bg-[#1c1c1e] border border-white/5 p-4 sm:p-5 rounded-xl sm:rounded-2xl text-xs sm:text-sm font-black font-headline text-white outline-none focus:border-primary/40 cursor-pointer appearance-none min-h-[48px]"
                  >
                      <option value="Gurgaon">Gurgaon Corridor</option>
                      <option value="Noida">Noida / Expressway</option>
                      <option value="Delhi">Delhi Core</option>
                  </select>
               </div>
            </div>
            <div className="space-y-4">
               <span className="text-[10px] font-black uppercase tracking-[0.4em] text-primary font-body">Yield Floor (%)</span>
               <input 
                  type="number" 
                  step="0.1" 
                  value={filters.min_yield} 
                  onChange={(e) => setFilters({...filters, min_yield: parseFloat(e.target.value) || 0})} 
                  className="w-full bg-[#1c1c1e] border border-white/5 p-4 sm:p-5 rounded-xl sm:rounded-2xl text-xs sm:text-sm font-black font-headline text-white outline-none focus:border-primary/40 min-h-[48px]" 
               />
            </div>
         </div>

         <button 
            onClick={handleDiscover} 
            disabled={loading} 
            className="w-full lg:w-72 bg-primary text-black font-black text-xs uppercase tracking-widest rounded-xl sm:rounded-2xl h-14 sm:h-16 flex items-center justify-center gap-4 hover:brightness-110 active:scale-95 transition-all shadow-xl shadow-primary/20 disabled:opacity-50"
         >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Radar className="w-6 h-6" />}
            Run Scanner
         </button>
      </div>

      {/* RESULT GRID */}
      {result && (
        <div className="space-y-12 sm:space-y-16 animate-in fade-in duration-1000">
           
           <div className="flex items-end justify-between border-b border-white/5 pb-8 sm:pb-10">
              <h2 className="text-3xl sm:text-4xl font-black font-headline uppercase tracking-tightest">
                Artifacts <span className="text-[#adaaab] font-light">[{result.summary.processed_assets}]</span>
              </h2>
           </div>

           <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-10 lg:gap-12 items-stretch">
              {result.featured_assets.map((asset, i) => (
                <div key={i} className="group bg-[#131314] rounded-[32px] sm:rounded-[48px] overflow-hidden transition-all duration-700 hover:-translate-y-2 shadow-2xl shadow-black/60 relative border border-white/5 flex flex-col justify-between">
                   
                   {/* Card Header Visual */}
                   <div className="h-40 sm:h-48 bg-[#1c1c1e] relative flex items-center justify-center overflow-hidden">
                       <div className="text-[80px] sm:text-[100px] font-black text-white/[0.03] uppercase select-none font-headline -rotate-6">
                          {asset.property_name.split(' ')[0]}
                       </div>
                       <div className="absolute top-6 left-6">
                          <div className="px-3 py-1 bg-black/40 backdrop-blur-3xl rounded-full border border-white/10 text-[8px] font-black text-primary uppercase tracking-widest">
                             {asset.type}
                          </div>
                       </div>
                   </div>

                   {/* Card Content */}
                   <div className="p-8 sm:p-10 space-y-8 flex flex-col flex-1 justify-between">
                      
                      <div className="flex justify-between items-start gap-4">
                         <div className="space-y-1">
                            <p className="text-[9px] font-black uppercase tracking-widest text-[#adaaab] font-body">{asset.sector}</p>
                            <h3 className="text-xl sm:text-2xl font-black font-headline leading-tight text-white">{asset.property_name}</h3>
                         </div>
                         <div className="w-10 h-10 sm:w-12 sm:h-12 bg-primary/10 text-primary rounded-xl flex items-center justify-center group-hover:bg-primary group-hover:text-black transition-all flex-shrink-0">
                            <ArrowUpRight className="w-5 h-5 sm:w-6 h-6" />
                         </div>
                      </div>

                      <div className="grid grid-cols-2 gap-6 py-6 border-y border-white/5">
                         <div className="space-y-1">
                            <span className="text-[9px] font-black uppercase tracking-[0.2em] text-[#adaaab] font-body">Alpha Score</span>
                            <p className="text-2xl sm:text-3xl font-black font-headline text-primary">
                               {asset.intelligence.alpha_score.toFixed(1)}
                            </p>
                         </div>
                         <div className="space-y-1">
                            <span className="text-[9px] font-black uppercase tracking-[0.2em] text-[#adaaab] font-body">Gross Yield</span>
                            <p className="text-2xl sm:text-3xl font-black font-headline text-green-400">
                               {asset.intelligence.financials.gross_yield.toFixed(1)}%
                            </p>
                         </div>
                      </div>

                      <div className="flex items-center justify-between pt-2">
                         <div className={`px-2.5 py-1 rounded-full text-[8px] font-black uppercase tracking-widest ${asset.intelligence.risk_label === 'VALUE PICK' ? 'bg-green-400/20 text-green-400' : 'bg-orange-400/20 text-orange-400'}`}>
                            {asset.intelligence.risk_label}
                         </div>
                         <p className="text-[9px] text-white/30 font-black tracking-widest uppercase">Institutional Hub</p>
                      </div>

                   </div>
                </div>
              ))}
           </div>
        </div>
      )}
    </div>
  );
}
