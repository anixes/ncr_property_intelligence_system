'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import ValuationBlock from '@/components/analyzer/ValuationBlock';
import { MapPin, ArrowLeft, Share2, Info, Building2, TrendingUp, Maximize, ShieldCheck, Bookmark } from 'lucide-react';
import Link from 'next/link';
import { formatCurrency, getMarketJudgment } from '@/lib/formatters';
import { generateNarrative } from '@/lib/generateNarrative';
import dynamic from 'next/dynamic';
import { useShortlist } from '@/hooks/useShortlist';

const SpatialMap = dynamic(() => import('@/components/maps/SpatialMap'), { ssr: false });

interface PropertyDetailPageProps {
  params: { id: string };
}

function PropertyDetailContent({ params }: PropertyDetailPageProps) {
  const searchParams = useSearchParams();
  const { toggleShortlist, isInShortlist } = useShortlist();
  
  const [propertyData, setPropertyData] = useState<any>(null);

  useEffect(() => {
    // Derive data from URL params for instant rendering
    const p = {
      society: searchParams.get('s') || 'Premium Asset',
      locality: searchParams.get('l') || 'NCR Sector',
      city: searchParams.get('c') || 'NCR',
      price: Number(searchParams.get('p')) || 18000000,
      area: Number(searchParams.get('a')) || 1800,
      bhk: Number(searchParams.get('b')) || 3,
      yield_pct: Number(searchParams.get('y')) || 0.032,
      valuation_pct: Number(searchParams.get('v')) || -0.05,
      unified_score: 8.4,
      listing_type: 'buy',
      price_per_sqft: (Number(searchParams.get('p')) || 18000000) / (Number(searchParams.get('a')) || 1800)
    };
    setPropertyData(p);
  }, [searchParams]);

  if (!propertyData) return <div className="p-20 text-center uppercase font-black text-slate-400">Syncing Intelligence...</div>;

  const narrative = generateNarrative({
    society: propertyData.society,
    locality: propertyData.locality,
    bhk: propertyData.bhk,
    valuationPct: propertyData.valuation_pct,
    yieldPct: propertyData.yield_pct
  });

  const isSaved = isInShortlist(propertyData);

  return (
    <div className="min-h-screen bg-transparent pb-24">
      
      {/* Institutional Telemetry Header */}
      <div className="glass-panel sticky top-20 z-40 px-6 lg:px-12 py-5 shadow-2xl shadow-primary/10 border-b border-white/5">
        <div className="max-w-[1400px] mx-auto flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/discover" className="p-2.5 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors">
               <ArrowLeft className="w-5 h-5 text-white/40" />
            </Link>
            <div>
               <h1 className="text-2xl font-black text-white uppercase tracking-tighter flex items-center gap-3 text-ellipsis overflow-hidden whitespace-nowrap lg:max-w-md">
                 {propertyData.society}
                 <span className={`intel-badge-glass !bg-transparent !border-current ${narrative.judgment.color}`}>
                    {narrative.judgment.icon} {narrative.judgment.label}
                 </span>
               </h1>
               <div className="flex items-center gap-2 label-eyebrow mt-1">
                 <MapPin className="w-3 h-3 text-primary" /> {propertyData.locality}, {propertyData.city}
               </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
             <button onClick={() => toggleShortlist(propertyData)} className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-[11px] font-black uppercase tracking-widest transition-all ${isSaved ? 'bg-primary text-white shadow-lg shadow-primary/30' : 'bg-white/5 text-white/40 border border-white/10 hover:bg-white/10'}`}>
                <Bookmark className={`w-3.5 h-3.5 ${isSaved ? 'fill-current' : ''}`} /> {isSaved ? 'Bookmarked' : 'Shortlist'}
             </button>
             <button className="flex items-center gap-2 px-6 py-2.5 bg-transparent border border-white/10 rounded-xl text-[11px] font-black uppercase tracking-widest text-white/40 hover:bg-white/5 transition-all">
                <Share2 className="w-3.5 h-3.5" /> Share Report
             </button>
          </div>
        </div>
      </div>

      <div className="max-w-[1400px] mx-auto px-6 lg:px-12 mt-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
           
           <div className="lg:col-span-12 xl:col-span-8 flex flex-col gap-12">
              <div className="institutional-card p-1">
                <ValuationBlock 
                  marketValue={propertyData.price}
                  intelligence={{ overvaluation_pct: propertyData.valuation_pct } as any}
                  label="Current Analytical Valuation"
                />
              </div>

              <div className="institutional-card p-12 relative overflow-hidden">
                 <div className="absolute top-0 right-0 p-8 opacity-[0.05]">
                    <ShieldCheck className="w-24 h-24 text-primary" />
                 </div>
                 <h2 className="label-eyebrow mb-8">
                    Institutional Narrative & Intelligence
                 </h2>
                 <div className="text-xl font-bold text-white/80 leading-relaxed max-w-3xl whitespace-pre-wrap">
                    {narrative.body}
                 </div>
              </div>

              <div className="institutional-card p-2 h-[500px] overflow-hidden relative">
                 <div className="absolute top-8 left-8 z-20 px-4 py-2 bg-black/60 backdrop-blur-xl rounded-xl border border-white/10 shadow-2xl">
                    <span className="text-[10px] font-black text-white uppercase tracking-widest">Localized Spatial Intel</span>
                 </div>
                 <SpatialMap listings={[]} />
              </div>
           </div>

           <div className="lg:col-span-12 xl:col-span-4 flex flex-col gap-12">
              <div className="institutional-card p-10 flex flex-col gap-8">
                 <div className="flex flex-col gap-2">
                    <span className="label-eyebrow">Inventory Profile</span>
                    <div className="flex items-center gap-3">
                       <Maximize className="w-5 h-5 text-primary" />
                       <span className="text-2xl font-black text-white">{propertyData.area} SQFT <span className="text-white/40 ml-1">{propertyData.bhk} BHK</span></span>
                    </div>
                 </div>

                 <div className="grid grid-cols-2 gap-8 pt-8 border-t border-white/5">
                    <div className="flex flex-col gap-1.5">
                       <span className="label-eyebrow">Estimated Yield</span>
                       <span className="text-xl font-black text-emerald-400">{(propertyData.yield_pct * 100).toFixed(2)}%</span>
                    </div>
                    <div className="flex flex-col gap-1.5">
                       <span className="label-eyebrow">Asset Exposure</span>
                       <span className="text-xl font-black text-white">₹{Math.round(propertyData.price_per_sqft).toLocaleString('en-IN')}</span>
                    </div>
                 </div>
              </div>

              <div className="bg-primary/10 backdrop-blur-2xl border border-primary/20 rounded-[40px] p-10 text-white shadow-2xl shadow-primary/5">
                 <h3 className="label-eyebrow mb-6 text-primary/80">Strategic Allocation Performance</h3>
                 <div className="space-y-6">
                    <div className="flex justify-between items-center">
                       <span className="text-xs font-bold uppercase tracking-widest text-white/60">Institutional Liquidity</span>
                       <span className="text-lg font-black tracking-tighter text-white">Tier A</span>
                    </div>
                    <div className="flex justify-between items-center">
                       <span className="text-xs font-bold uppercase tracking-widest text-white/60">Area Potential (3Y)</span>
                       <span className="text-lg font-black tracking-tighter text-emerald-400">+12.4%</span>
                    </div>
                    <div className="p-4 bg-white/5 rounded-2xl mt-4 border border-white/5">
                       <p className="text-[10px] leading-relaxed font-medium text-white/40 uppercase tracking-wider italic">
                         "Asset maintains high adjacency to peripheral infrastructure nodes, positioning for structural appreciation."
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

export default function PropertyDetailPage({ params }: PropertyDetailPageProps) {
  return (
    <Suspense fallback={<div className="p-20 text-center uppercase font-black text-slate-400">Loading Report Architecture...</div>}>
      <PropertyDetailContent params={params} />
    </Suspense>
  );
}
