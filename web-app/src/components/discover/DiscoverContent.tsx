'use client';

import { Suspense, useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useDiscover } from '@/hooks/useDiscover';
import FilterBar from '@/components/discover/FilterBar';
import ResultsGrid from '@/components/discover/ResultsGrid';
import dynamic from 'next/dynamic';
import { Map as MapIcon, LayoutGrid, Search as SearchIcon, ChevronDown, Zap, Globe, Target } from 'lucide-react';
import { DiscoverRequest } from '@/types';

const SpatialMap = dynamic(() => import('@/components/maps/SpatialMap'), { ssr: false });

export default function DiscoverContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { data: listings, isLoading, error, mutate: search } = useDiscover();
  const [viewMode, setViewMode] = useState<'grid' | 'map'>('grid');

  // Initial State from URL
  const [currentFilters, setCurrentFilters] = useState<DiscoverRequest>({
    city: searchParams.get('city') || 'Gurgaon',
    listing_type: (searchParams.get('type') as any) || 'buy',
    bhk: searchParams.get('bhk') ? searchParams.get('bhk')!.split(',').map(Number) : [2, 3],
    budget_min: Number(searchParams.get('min')) || 50,
    budget_max: Number(searchParams.get('max')) || 300,
  });

  useEffect(() => {
    const fromUrl = {
      city: searchParams.get('city') || 'Gurgaon',
      listing_type: (searchParams.get('type') as any) || 'buy',
      bhk: searchParams.get('bhk') ? searchParams.get('bhk')!.split(',').map(Number) : [2, 3],
      budget_min: Number(searchParams.get('min')) || 50,
      budget_max: Number(searchParams.get('max')) || 300,
    };
    
    setCurrentFilters(fromUrl);
    search(fromUrl);
  }, [searchParams]);

  const handleSearch = (filters: DiscoverRequest) => {
    const params = new URLSearchParams();
    params.set('city', filters.city);
    params.set('type', filters.listing_type);
    params.set('bhk', filters.bhk.join(','));
    params.set('min', filters.budget_min.toString());
    params.set('max', filters.budget_max.toString());
    
    router.replace(`/discover?${params.toString()}`, { scroll: false });
  };

  return (
    <div className="flex-1 w-full min-h-screen bg-background text-foreground relative overflow-hidden pt-24 pb-24">
      {/* --- BLUEPRINT SUBSTRATE --- */}
      <div className="absolute inset-0 bg-[#050505]">
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />
        <div className="absolute inset-x-0 top-0 h-96 bg-gradient-to-b from-primary/10 to-transparent blur-[120px]" />
      </div>

      <div className="relative z-10 max-w-[1800px] mx-auto px-6">
        
        {/* --- HEADER: COMMAND CONTROL --- */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-end mb-16 gap-12">
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <div className="px-3 py-1 bg-primary/10 border border-primary/20 rounded-full text-[10px] font-black text-primary uppercase tracking-[0.3em]">
                Acquisitions Node
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                <span className="text-[10px] font-black text-white/40 uppercase tracking-widest">Live Engine</span>
              </div>
            </div>
            
            <h1 className="text-6xl lg:text-8xl font-black tracking-tight text-white uppercase leading-none">
              DISCOVERY <br /> <span className="text-white/20">ENGINE</span>
            </h1>
            
            <p className="text-white/40 max-w-xl text-xs font-black uppercase tracking-widest leading-relaxed">
              Scanning 43,000+ verified institutional market records. <br />
              Identify geometric yields and undervalued strategic outliers.
            </p>
          </div>

          <div className="flex items-center gap-3 p-1.5 bg-white/[0.03] border border-white/5 rounded-2xl backdrop-blur-3xl shadow-2xl">
            <button 
              onClick={() => setViewMode('grid')}
              className={`flex items-center gap-3 px-8 py-4 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] transition-all ${viewMode === 'grid' ? 'bg-primary text-white shadow-xl shadow-primary/40' : 'text-white/20 hover:text-white/60'}`}
            >
              <LayoutGrid className="w-4 h-4" /> Grid
            </button>
            <button 
              onClick={() => setViewMode('map')}
              className={`flex items-center gap-3 px-8 py-4 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] transition-all ${viewMode === 'map' ? 'bg-primary text-white shadow-xl shadow-primary/40' : 'text-white/20 hover:text-white/60'}`}
            >
              <MapIcon className="w-4 h-4" /> Spatial
            </button>
          </div>
        </div>

        {/* --- FILTER INTERFACE --- */}
        <section className="mb-12">
          <FilterBar onSearch={handleSearch} isLoading={isLoading} initialFilters={currentFilters} />
        </section>

        {/* --- MAIN RESULTS DECK --- */}
        <div className="bg-white/[0.02] border border-white/[0.05] rounded-[48px] backdrop-blur-3xl p-12 min-h-[800px] shadow-3xl relative overflow-hidden">
          {/* Deck Metadata */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-16 pb-12 border-b border-white/[0.05] gap-8">
            <div className="flex flex-col gap-4">
              <span className="text-[10px] font-black text-white/40 uppercase tracking-[0.4em]">Current Vector</span>
              <div className="flex items-center gap-6">
                <h3 className="text-2xl font-black text-white uppercase tracking-tighter">
                  {currentFilters.city} Market Pool
                </h3>
                <div className="px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-[9px] font-black text-emerald-400 uppercase tracking-widest">
                  {listings.length} High-Yield Signals
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-6">
              <div className="flex flex-col items-end gap-2">
                <span className="text-[9px] font-black text-white/20 uppercase tracking-widest">Sorting Model</span>
                <select className="bg-white/[0.05] border border-white/5 text-[10px] font-black uppercase tracking-[0.2em] text-white rounded-xl px-6 py-3 focus:ring-2 focus:ring-primary/40 cursor-pointer outline-none transition-all hover:bg-white/[0.08]">
                  <option>Decision Score</option>
                  <option>Yield Variance</option>
                  <option>Value Delta</option>
                </select>
              </div>
            </div>
          </div>
          
          {/* Deck Viewport */}
          {isLoading ? (
            <div className="h-[600px] flex flex-col items-center justify-center gap-12">
              <div className="relative w-24 h-24">
                <div className="absolute inset-0 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
                <div className="absolute inset-4 border border-white/5 border-b-white/40 rounded-full animate-pulse" />
              </div>
              <div className="text-center space-y-4">
                <h2 className="text-xl font-black text-white uppercase tracking-[1em] animate-pulse">Syncing HUD</h2>
                <p className="text-[10px] font-black text-white/20 uppercase tracking-[0.5em]">Aggregating Spatial Cells</p>
              </div>
            </div>
          ) : viewMode === 'grid' ? (
            <ResultsGrid 
              listings={listings} 
              isLoading={isLoading} 
              error={error} 
            />
          ) : (
            <div className="h-[800px] w-full rounded-[32px] overflow-hidden border border-white/10 shadow-inner group transition-all duration-700 hover:border-primary/40 relative">
               {/* Map Protection Overlay */}
               <div className="absolute top-6 left-6 z-20 flex flex-col gap-4">
                  <div className="p-4 bg-black/80 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-3xl w-64 space-y-6">
                     <div>
                        <span className="text-[9px] font-black text-white/40 uppercase tracking-widest block mb-3">Map Resolution</span>
                        <div className="grid grid-cols-2 gap-2">
                           <button className="px-3 py-2 bg-primary text-white text-[9px] font-black rounded-lg uppercase tracking-widest">H3 Res-8</button>
                           <button className="px-3 py-2 bg-white/5 text-white/40 text-[9px] font-black rounded-lg uppercase tracking-widest">Res-9</button>
                        </div>
                     </div>
                     <div className="pt-4 border-t border-white/5">
                        <button className="w-full py-3 bg-white/5 text-white/60 text-[9px] font-black rounded-lg uppercase tracking-[0.2em] border border-white/5 hover:bg-white/10 transition-all">
                           Export Lat/Long
                        </button>
                     </div>
                  </div>
               </div>
              <SpatialMap listings={listings} city={currentFilters.city} />
            </div>
          )}
        </div>
      </div>

      {/* --- FLOATING STATUS HUB --- */}
      <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-[200] hidden lg:flex items-center gap-8 px-8 py-4 bg-black/80 border border-white/10 rounded-full backdrop-blur-2xl shadow-3xl">
         <div className="flex items-center gap-3">
            <Target className="w-4 h-4 text-primary" />
            <span className="text-[10px] font-black text-white/40 uppercase tracking-widest">Targeting: <span className="text-white">{currentFilters.city}</span></span>
         </div>
         <div className="h-4 w-px bg-white/10" />
         <div className="flex items-center gap-3 text-[10px] font-black text-white/40 uppercase tracking-widest">
            <Globe className="w-4 h-4 text-emerald-500" />
            Node: <span className="text-emerald-500">Gurgaon_Central_01</span>
         </div>
         <div className="h-4 w-px bg-white/10" />
         <div className="flex items-center gap-3 text-[10px] font-black text-white/40 uppercase tracking-widest">
            <Zap className="w-4 h-4 text-primary" />
            Latency: <span className="text-primary">12ms</span>
         </div>
      </div>
    </div>
  );
}
