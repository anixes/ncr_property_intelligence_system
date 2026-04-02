'use client';

import { Suspense } from 'react';
import ValuationBlock from '@/components/analyzer/ValuationBlock';
import { MapPin, ArrowLeft, Share2, Maximize, ShieldCheck, Bookmark, TrendingUp, Gauge } from 'lucide-react';
import Link from 'next/link';
import { formatCurrency } from '@/lib/formatters';
import { generateNarrative } from '@/lib/generateNarrative';
import dynamic from 'next/dynamic';
import { useShortlist } from '@/hooks/useShortlist';
import { cn } from '@/lib/utils';

const SpatialMap = dynamic(() => import('@/components/maps/SpatialMap'), { ssr: false });

interface PropertyDetailClientProps {
  propertyData: any;
}

export default function PropertyDetailClient({ propertyData }: PropertyDetailClientProps) {
  const { toggleShortlist, isInShortlist } = useShortlist();
  const isSaved = isInShortlist(propertyData);

  // Institutional Narrative Sync
  const narrative = generateNarrative({
    society: propertyData.society,
    locality: propertyData.locality,
    bhk: propertyData.bhk,
    valuationPct: propertyData.valuation_pct || propertyData.delta,
    yieldPct: propertyData.yield_pct
  });

  return (
    <div className="min-h-screen bg-slate-50/50 pb-24">
      
      {/* Institutional Progress Header */}
      <div className="bg-white/80 backdrop-blur-xl border-b border-slate-100 sticky top-16 z-40 px-6 lg:px-12 py-5">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-6">
          <div className="flex items-center gap-6 min-w-0">
            <Link href="/discover" className="p-3 bg-slate-50 border border-slate-100 rounded-2xl hover:bg-white hover:border-primary/20 transition-all group">
               <ArrowLeft className="w-5 h-5 text-slate-400 group-hover:text-primary transition-colors" />
            </Link>
            <div className="min-w-0">
               <div className="flex items-center gap-3">
                 <h1 className="text-xl md:text-2xl font-black text-slate-900 uppercase tracking-tighter truncate">
                   {propertyData.society}
                 </h1>
                 <div className={cn(
                    "hidden sm:flex px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border shadow-sm shrink-0",
                    (propertyData.valuation_pct || propertyData.delta) <= 0 
                      ? "bg-emerald-50 text-emerald-700 border-emerald-100" 
                      : "bg-amber-50 text-amber-700 border-amber-100"
                 )}>
                    {narrative.judgment.icon} {narrative.judgment.label}
                 </div>
               </div>
               <div className="flex items-center gap-1.5 label-eyebrow text-[10px] mt-1">
                 <MapPin className="w-3 h-3 text-primary" /> {propertyData.locality}, {propertyData.city}
               </div>
            </div>
          </div>

          <div className="flex items-center gap-3 shrink-0">
             <button 
               onClick={() => toggleShortlist(propertyData)} 
               className={cn(
                 "flex items-center gap-2 px-6 py-3 rounded-2xl text-[11px] font-black uppercase tracking-widest transition-all",
                 isSaved 
                   ? "bg-primary text-white shadow-lg shadow-primary/20" 
                   : "bg-slate-50 text-slate-400 border border-slate-100 hover:bg-white hover:text-primary hover:border-primary/20"
               )}
             >
                <Bookmark className={cn("w-3.5 h-3.5", isSaved && "fill-current")} /> 
                <span className="hidden md:inline">{isSaved ? 'Bookmarked' : 'Shortlist'}</span>
             </button>
             <button className="hidden sm:flex items-center gap-2 px-6 py-3 bg-white border border-slate-100 rounded-2xl text-[11px] font-black uppercase tracking-widest text-slate-400 hover:border-primary/20 hover:text-primary transition-all">
                <Share2 className="w-3.5 h-3.5" /> <span className="hidden md:inline">Share Report</span>
             </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 lg:px-12 mt-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
           
           {/* Primary Analysis Column */}
           <div className="lg:col-span-8 flex flex-col gap-12">
              <ValuationBlock 
                marketValue={propertyData.price}
                intelligence={{ overvaluation_pct: propertyData.valuation_pct || propertyData.delta } as any}
                label="Portfolio Asset Valuation"
              />

              <div className="institutional-card bg-white p-10 md:p-14 relative overflow-hidden">
                 <div className="absolute -top-12 -right-12 p-8 opacity-[0.02] pointer-events-none">
                    <ShieldCheck className="w-64 h-64 text-primary" />
                 </div>
                 <h2 className="label-eyebrow text-slate-400 mb-10">
                    Proprietary Market Narrative
                 </h2>
                 <div className="text-xl md:text-2xl font-bold text-slate-600 leading-relaxed max-w-3xl whitespace-pre-wrap">
                    {narrative.body}
                 </div>
                 <div className="mt-12 flex items-center gap-3 pt-10 border-t border-slate-50">
                    <Gauge className="w-5 h-5 text-emerald-500" />
                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
                       Generated by NCR Market Intelligence Engine V4.2
                    </span>
                 </div>
              </div>

              <div className="institutional-card bg-white p-2 h-[500px] overflow-hidden relative group">
                 <div className="absolute top-8 left-8 z-20 px-5 py-2.5 bg-white/90 backdrop-blur-xl rounded-2xl border border-slate-100 shadow-2xl transition-transform group-hover:scale-105">
                    <span className="label-eyebrow text-slate-900">Localized Spatial Intel</span>
                 </div>
                 <SpatialMap listings={[propertyData]} city={propertyData.city} />
              </div>
           </div>

           {/* Performance Sidebar */}
           <div className="lg:col-span-4 flex flex-col gap-12 sticky top-48">
              <div className="institutional-card bg-white p-10 flex flex-col gap-10">
                 <div className="flex flex-col gap-3">
                    <span className="label-eyebrow text-slate-400">Yield Architecture</span>
                    <div className="flex items-end gap-3 px-1">
                       <span className="text-4xl font-black text-slate-900 tracking-tighter">
                          {(propertyData.yield_pct * 100).toFixed(2)}%
                       </span>
                       <span className="label-eyebrow text-emerald-600 pb-1.5 flex items-center gap-1">
                          <TrendingUp className="w-3 h-3" /> Yield
                       </span>
                    </div>
                 </div>

                 <div className="grid grid-cols-1 gap-8 pt-10 border-t border-slate-50">
                    <div className="flex flex-col gap-3">
                       <span className="label-eyebrow text-slate-400">Built Area Configuration</span>
                       <div className="flex items-center gap-4">
                          <div className="p-3 bg-slate-50 rounded-2xl text-primary">
                             <Maximize className="w-5 h-5" />
                          </div>
                          <span className="text-xl font-black text-slate-900">
                             {propertyData.area} <span className="text-slate-400 text-sm font-bold uppercase tracking-widest ml-1">sqft</span>
                          </span>
                       </div>
                    </div>
                    <div className="flex items-center gap-3 px-4 py-3 bg-slate-50 rounded-2xl">
                       <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Layout:</span>
                       <span className="text-sm font-black text-slate-900 uppercase tracking-tighter">{propertyData.bhk} Bedroom Suite</span>
                    </div>
                 </div>

                 <button className="btn-premium h-14 text-[10px] shadow-primary/10">
                    Download Full Performance Audit
                 </button>
              </div>

              <div className="bg-primary rounded-[40px] p-10 text-white shadow-2xl shadow-primary/20 relative overflow-hidden group">
                 <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-16 translate-x-16 blur-3xl group-hover:bg-white/10 transition-colors" />
                 <h3 className="label-eyebrow text-white/50 mb-8">Strategic Intelligence</h3>
                 <div className="space-y-8">
                    <div className="flex justify-between items-center pb-6 border-b border-white/10">
                       <span className="text-[10px] font-black uppercase tracking-widest text-white/60">Institutional Grade</span>
                       <span className="text-lg font-black tracking-tighter uppercase">Verified</span>
                    </div>
                    <div className="flex justify-between items-center">
                       <span className="text-[10px] font-black uppercase tracking-widest text-white/60">Area Liquidity</span>
                       <div className="flex items-center gap-2">
                          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                          <span className="text-lg font-black tracking-tighter">High Alpha</span>
                       </div>
                    </div>
                    <div className="p-6 bg-white/10 rounded-3xl mt-4 border border-white/5">
                       <p className="text-[10px] leading-relaxed font-black uppercase tracking-wider text-white/70 italic">
                          "Underlying infrastructure growth vector identifies this asset as a core capital appreciation target for 2026."
                       </p>
                    </div>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
