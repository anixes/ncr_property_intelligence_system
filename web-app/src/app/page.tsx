"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  Search, 
  Map as MapIcon, 
  ChevronRight, 
  ArrowUpRight,
  TrendingUp,
  Zap,
  Shield
} from "lucide-react";
import { getHotspots } from "@/lib/api";
import { Hotspot } from "@/types";

export default function InstitutionalTerminal() {
  const [searchFocused, setSearchFocused] = useState(false);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function init() {
      try {
        const data = await getHotspots("Gurgaon", "buy");
        setHotspots(data.slice(0, 3));
      } catch (e) {
        console.error("API Sync Failed", e);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  return (
    <main className="relative min-h-screen pt-20 pb-32 overflow-hidden bg-background">
      {/* --- HERO: ARCHITECTURAL BACKDROP --- */}
      <div className="absolute inset-0 z-0 pointer-events-none opacity-20">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background to-background z-10" />
        <img 
          src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&q=80&w=2000" 
          alt="Architectural Backdrop"
          className="object-cover w-full h-full grayscale brightness-50"
        />
      </div>

      <div className="relative z-10 px-6 mx-auto max-w-7xl">
        
        {/* --- SECTION 1: SEARCH PORTER --- */}
        <section className="flex flex-col items-center justify-center py-24 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-power-hero mb-6">
              Search<br />Porter
            </h1>
            <p className="text-white/40 font-bold uppercase tracking-[0.3em] text-[10px] mb-12">
              Select a Sector, Building, or Address...
            </p>
            
            <div className={`relative max-w-2xl mx-auto transition-all duration-500 transform ${searchFocused ? 'scale-105' : 'scale-100'}`}>
              <div className={`absolute -inset-2 rounded-3xl bg-primary/20 blur-3xl transition-opacity duration-500 ${searchFocused ? 'opacity-100' : 'opacity-0'}`} />
              <div className="relative flex items-center bg-white/[0.03] backdrop-blur-3xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl transition-colors hover:bg-white/[0.05]">
                <Search className="ml-6 text-white/40" size={20} />
                <input 
                  type="text" 
                  placeholder="Gurgaon Sectors, Noida Buildings..."
                  className="w-full h-20 px-6 text-xl font-medium text-white placeholder-white/20 bg-transparent outline-none"
                  onFocus={() => setSearchFocused(true)}
                  onBlur={() => setSearchFocused(false)}
                />
                <button className="h-16 w-16 mr-2 flex items-center justify-center text-white transition-all bg-primary rounded-xl hover:bg-primary/80 shadow-lg shadow-primary/20">
                  <ArrowUpRight size={24} />
                </button>
              </div>
            </div>
          </motion.div>
        </section>

        {/* --- SECTION 2: IN MARKETS (QUICK FEED) --- */}
        <section className="mt-20">
          <div className="flex items-end justify-between mb-12">
            <div>
              <span className="label-eyebrow">Institutional Alpha</span>
              <h2 className="text-4xl font-black text-white mt-2 uppercase tracking-tighter">In Markets</h2>
            </div>
            <button className="flex items-center gap-2 text-primary font-black uppercase tracking-widest text-[10px] hover:translate-x-2 transition-transform">
              View All Intelligence <ChevronRight size={16} />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {hotspots.length > 0 ? hotspots.map((property, idx) => (
              <motion.div 
                key={`${property.locality}-${idx}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                className="institutional-card group"
              >
                <div className="relative h-64 overflow-hidden">
                  <img 
                    src={`https://images.unsplash.com/photo-1545324418-f1d3c5b5a572?auto=format&fit=crop&q=80&w=800&h=600&sig=${idx}`} 
                    className="object-cover w-full h-full transition-transform duration-1000 group-hover:scale-110 grayscale group-hover:grayscale-0"
                    alt={property.locality}
                  />
                  <div className="absolute top-4 left-4 flex gap-2">
                    <span className="intel-badge">Value Score: {property.score}</span>
                    <span className="intel-badge-glass">ROI: +{property.growth_potential}%</span>
                  </div>
                </div>
                <div className="p-8">
                  <div className="flex justify-between items-start mb-6">
                    <div>
                      <h3 className="text-2xl font-black text-white tracking-tighter leading-tight mb-2">{property.locality}</h3>
                      <p className="text-white/40 text-[10px] font-black uppercase tracking-[0.2em]">{property.city} • Institutional Grade</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xl font-black text-white leading-none">₹{(property.median_price / 10000000).toFixed(1)} Cr</p>
                      <p className="text-[9px] font-black text-white/30 uppercase tracking-widest mt-1">Avg Asset</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-4 pt-6 mt-6 border-t border-white/[0.05]">
                    <div>
                      <p className="label-eyebrow mb-1">Yield</p>
                      <p className="text-xs font-black text-white">4.8%</p>
                    </div>
                    <div>
                      <p className="label-eyebrow mb-1">Growth</p>
                      <p className="text-xs font-black text-primary">High</p>
                    </div>
                    <div>
                      <p className="label-eyebrow mb-1">Risk</p>
                      <p className="text-xs font-black text-white">Low</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            )) : (
              [1, 2, 3].map(i => (
                <div key={i} className="h-96 rounded-[var(--radius-card)] bg-white/5 animate-pulse" />
              ))
            )}
          </div>
        </section>

        {/* --- SECTION 3: INTELLIGENCE BENTO GRID --- */}
        <section className="mt-32">
          <div className="bento-grid">
            
            {/* LARGE QUAD: SPATIAL INTELLIGENCE */}
            <div className="md:col-span-3 md:row-span-2 bento-item group p-0 overflow-hidden relative border-primary/20 bg-slate-950">
              <div className="p-10 relative z-10">
                <MapIcon className="text-primary mb-6" size={32} />
                <h3 className="text-3xl font-black text-white uppercase tracking-tighter mb-4">Spatial Intelligence</h3>
                <p className="text-white/50 text-sm leading-relaxed max-w-sm">
                  Neural analysis of transit nodes, absorption metrics, and asset-level appreciation velocity.
                </p>
              </div>
              
              <div className="absolute inset-0 z-0 pointer-events-none">
                 <div className="absolute inset-0 bg-primary/5 [mask-image:radial-gradient(ellipse_at_center,black,transparent_70%)]" />
                 <div className="grid grid-cols-12 h-full opacity-20">
                    {Array.from({length: 144}).map((_, i) => (
                      <div key={i} className="border-[0.5px] border-white/5" />
                    ))}
                 </div>
                 <div className="absolute bottom-0 left-0 right-0 h-48 bg-gradient-to-t from-slate-950 to-transparent" />
              </div>
              
              <div className="absolute bottom-10 left-10 p-4 rounded-xl bg-primary/20 border border-primary/30 backdrop-blur-xl">
                 <span className="text-[10px] font-black uppercase tracking-[0.3em] text-white">Engine Online v4.2</span>
              </div>
            </div>

            {/* HIGH-CAPS STATS */}
            <div className="md:col-span-3 bento-item bg-white/[0.02]">
              <div className="flex justify-between items-start">
                <div>
                   <span className="label-eyebrow text-primary">Institutional Access</span>
                   <p className="text-xl font-bold text-white mt-4 max-w-xs leading-snug">
                     Capital inflow detected in Gurgaon Sector 54 Institutional Belt.
                   </p>
                </div>
                <TrendingUp className="text-primary" size={24} />
              </div>
              <div className="flex items-center gap-4 mt-8">
                <div className="flex -space-x-3">
                  {[1,2,3,4].map(i => <div key={i} className="w-10 h-10 rounded-full border-4 border-background bg-slate-800" />)}
                </div>
                <span className="text-[10px] font-black uppercase tracking-widest text-white/30">Analysts Active Recently</span>
              </div>
            </div>

            {/* VALUE METRIC */}
            <div className="md:col-span-1 bento-item text-center items-center justify-center border-white/5">
               <div className="text-4xl font-black text-white tracking-widest">₹8.2K Cr</div>
               <p className="label-eyebrow text-white/40 mt-4">Liquidity Swept</p>
            </div>

            {/* GROWTH CTA */}
            <div className="md:col-span-2 bento-item bg-primary/10 border-primary/40 group relative overflow-hidden">
               <div className="absolute -right-10 -bottom-10 w-40 h-40 bg-primary/20 blur-[100px] group-hover:scale-150 transition-transform duration-1000" />
               <div className="relative z-10 h-full flex flex-col justify-between">
                  <div>
                    <h4 className="text-5xl font-black text-white">13m+</h4>
                    <p className="label-eyebrow text-white/60 mt-1">Acres Appraised</p>
                  </div>
                  <button className="w-full py-4 bg-primary text-white font-black uppercase tracking-widest text-[10px] rounded-xl hover:bg-white hover:text-primary transition-all shadow-xl shadow-primary/20">
                    Generate Alpha Report
                  </button>
               </div>
            </div>

          </div>
        </section>

      </div>
      
      {/* --- PERSISTENT MARKET PULSE --- */}
      <div className="fixed bottom-0 left-0 right-0 h-16 bg-background/80 backdrop-blur-3xl border-t border-white/5 z-50 flex items-center overflow-hidden">
        <div className="animate-ticker flex gap-16 text-white/30 text-[10px] font-black uppercase tracking-[0.3em] px-12">
          {[...['Gurgaon Sec-54: +12.4%', 'Noida Sec-150: Bullish', 'DLF Phase 5: Low Inventory', 'G. Noida: Buy Signal', 'Macro: Repo Rate Stable'], ...['Gurgaon Sec-54: +12.4%', 'Noida Sec-150: Bullish', 'DLF Phase 5: Low Inventory', 'G. Noida: Buy Signal', 'Macro: Repo Rate Stable']].map((t, i) => (
            <span key={`ticker-${i}`} className="flex items-center gap-4 whitespace-nowrap">
              <span className="w-2 h-2 rounded-full bg-primary shadow-[0_0_12px_var(--brand-purple)]" />
              {t}
            </span>
          ))}
        </div>
      </div>
    </main>
  );
}
