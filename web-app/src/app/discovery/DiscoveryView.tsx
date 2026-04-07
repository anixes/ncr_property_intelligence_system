'use client';


import React, { useState, useEffect, useCallback, useRef } from 'react';
import { discoverProperties } from '@/lib/api';
import { DiscoverRequest, PropertyAsset, Recommendation } from '@/types';
import { PropertyCard } from '@/components/dashboard/PropertyCard';
import { PropertyDeepDive } from '@/components/dashboard/PropertyDeepDive';
import { 
  Loader2, Radar, Target, MapPin, Building, Ruler, Settings2, 
  ChevronDown, Sparkles, Waves, Dumbbell, ShieldCheck, Zap, 
  TrainFront, Compass, Trees, Split, Crown, BookOpen, Wifi, 
  ArrowUpToLine, LayoutPanelLeft, Box, Construction, UserPlus,
  Coins, Wallet
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { InstitutionalSelect } from '@/components/dashboard/InstitutionalSelect';
import { InputPorter, Toggle, PropertyCommandCard } from '@/components/dashboard/PortalUI';

export default function DiscoveryView() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<(PropertyAsset | Recommendation)[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [mounted, setMounted] = useState(false);
  const advancedRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (showAdvanced) {
      setTimeout(() => {
        advancedRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 150);
    }
  }, [showAdvanced]);

  useEffect(() => {
    setMounted(true);
  }, []);
  
  // Detail Drawer State
  const [selectedItem, setSelectedItem] = useState<PropertyAsset | Recommendation | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const [filters, setFilters] = useState<DiscoverRequest>({
    city: 'Noida',
    listing_type: 'buy',
    bhk: [2, 3],
    budget_min: 5000000,
    budget_max: 50000000,
    area_min: 1000,
    area_max: 5000,
    sort_by: 'score',
    prop_type: 'Apartment',
    amenities: { has_pool: false, has_gym: false, has_lift: true, has_power_backup: true, is_gated_community: true, has_clubhouse: false, has_maintenance: false, has_wifi: false, is_high_ceiling: false },
    location_features: { is_near_metro: false, is_corner_property: false, is_park_facing: false, is_vastu_compliant: false },
    property_features: { is_luxury: false, is_servant_room: false, is_study_room: false, is_store_room: false, is_pooja_room: false, is_new_construction: false }
  });

  const handleDiscover = async () => {
    setLoading(true);
    try {
      const data = await discoverProperties(filters);
      setResults(data);
    } catch (e) { 
      console.error("Discovery failed", e); 
    } finally { 
      setLoading(false); 
    }
  };

  // Initial scan & context auto-fetch on intent change
  useEffect(() => {
    handleDiscover();
  }, [filters.listing_type]);

  const handleCardClick = useCallback((item: any) => {
    setSelectedItem(item);
    setIsDrawerOpen(true);
  }, []);

  return (
    <div className="w-full max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 pt-28 pb-12 sm:pt-32 sm:pb-20 lg:pt-36 lg:pb-24 space-y-16" suppressHydrationWarning>
      
      {/* INSTITUTIONAL HEADER & COMMAND CENTER */}
      <div className="space-y-12 max-w-5xl">
          <header className="space-y-8">
            <div className="flex justify-start">
              <div className="inline-flex items-center gap-3 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-[10px] font-black uppercase tracking-[0.4em] border border-primary/10 font-body">
                 Best Deals Search Engine
              </div>
            </div>
            
            <div className="space-y-4">
              <h1 className="text-3xl sm:text-5xl lg:text-8xl font-black font-headline tracking-tightest leading-[0.85] text-white">
                 Property <br className="hidden sm:block"/>
                 <span className="text-[#adaaab]">Search.</span>
              </h1>
              
              <p className="text-base sm:text-lg md:text-2xl text-[#adaaab] font-light max-w-2xl leading-relaxed tracking-tight font-body italic">
                 Find properties that match your exact criteria, ranked by our smart algorithms to ensure you get the absolute best value.
              </p>
            </div>
          </header>
      </div>
      
      {/* DISCOVERY PORTER (COMMAND CENTER) */}
      <div className="relative group max-w-5xl mx-auto">
        <div className="absolute -inset-1 bg-gradient-to-r from-primary/5 via-primary/10 to-primary/5 rounded-[2.5rem] blur-2xl opacity-0 group-hover:opacity-100 transition-all duration-1000" />
        
        <div className="relative bg-[#0a0a0a]/80 backdrop-blur-3xl border border-white/5 rounded-2xl sm:rounded-[2rem] lg:rounded-[2.5rem] p-4 sm:p-10 lg:p-12 space-y-6 sm:space-y-8 overflow-hidden">
           
           {/* 1. INTENT SELECTOR & ADVANCED TOGGLE */}
            <div className="flex items-center justify-between gap-4">
               <div className="inline-flex p-1 bg-white/[0.02] border border-white/5 rounded-xl gap-1">
                   {['buy', 'rent'].map((t) => (
                     <button
                       key={t}
                       onClick={() => {
                         if (t === filters.listing_type) return;
                         const isBuy = t === 'buy';
                         setFilters({ 
                           ...filters, 
                           listing_type: t as any,
                           budget_min: isBuy ? 2000000 : 10000,
                           budget_max: isBuy ? 50000000 : 200000,
                           sort_by: (!isBuy && filters.sort_by === 'yield') ? 'score' : filters.sort_by
                         });
                       }}
                       className={`px-5 sm:px-8 py-2 rounded-lg text-[9px] font-black uppercase tracking-[0.1em] transition-all duration-300 active:scale-95 ${
                         filters.listing_type === t 
                           ? 'bg-primary text-black shadow-[0_0_15px_rgba(189,157,255,0.2)]' 
                           : 'text-[#adaaab] hover:text-white hover:bg-white/5'
                       }`}
                     >
                       {t}
                     </button>
                   ))}
               </div>
               
               <button 
                 onClick={() => setShowAdvanced(!showAdvanced)}
                 className="flex items-center gap-2.5 px-4 h-10 rounded-xl bg-white/[0.03] border border-white/5 text-[#adaaab] font-black text-[9px] uppercase tracking-widest hover:bg-white/[0.06] active:scale-95 transition-all outline-none"
               >
                 <Settings2 className="w-3.5 h-3.5" />
                 <span>Advanced</span>
                 <ChevronDown className={`w-3 h-3 transition-transform duration-500 ${showAdvanced ? 'rotate-180' : ''}`} />
               </button>
            </div>

            {/* 2. UNIFIED COMMAND GRID */}
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-8 lg:gap-10">
               <InputPorter 
                 label="City"
                 value={filters.city}
                 onChange={(v) => setFilters({...filters, city: v})}
                 icon={MapPin}
                 type="select"
                 options={['Gurgaon', 'Noida', 'Delhi', 'Ghaziabad', 'Faridabad']}
                 className="col-span-1"
               />
               
               <InputPorter 
                 label="Type"
                 value={filters.prop_type}
                 onChange={(v) => setFilters({...filters, prop_type: v})}
                 icon={Building}
                 type="select"
                 options={['Any', 'Apartment', 'Builder Floor', 'Independent House']}
                 className="col-span-1"
               />

               <InputPorter 
                 label="BHK"
                 value={(filters.bhk || [2, 3]).map(String)}
                 onChange={(v) => setFilters({...filters, bhk: Array.isArray(v) ? v.map(Number) : [Number(v)]})}
                 icon={Split}
                 type="segmented"
                 options={['1', '2', '3', '4', '5']}
                 className="col-span-2 lg:col-span-1"
               />

               <InputPorter 
                 label={filters.listing_type === 'buy' ? "Budget" : "Rent"}
                 value={[filters.budget_min, filters.budget_max]}
                 onChange={([min, max]) => setFilters({...filters, budget_min: min, budget_max: max})}
                 icon={Coins}
                 type="range"
                 min={filters.listing_type === 'buy' ? 2000000 : 5000}
                 max={filters.listing_type === 'buy' ? 100000000 : 500000}
                 step={filters.listing_type === 'buy' ? 500000 : 1000}
                 placeholder={
                   filters.listing_type === 'buy' 
                     ? `${(filters.budget_min / 100000).toFixed(0)}L - ${(filters.budget_max / 10000000).toFixed(1)}Cr`
                     : `₹${(filters.budget_min / 1000).toFixed(0)}K-₹${(filters.budget_max / 1000).toFixed(0)}K`
                 }
                 className="col-span-2 lg:col-span-1"
               />

               <InputPorter 
                 label="Area"
                 value={[filters.area_min, filters.area_max]}
                 onChange={([min, max]) => setFilters({...filters, area_min: min, area_max: max})}
                 icon={Ruler}
                 type="range"
                 min={500}
                 max={10000}
                 step={100}
                 placeholder={`${filters.area_min}-${filters.area_max} SqFt`}
                 className="col-span-2 lg:col-span-1"
               />

               <InputPorter 
                 label="Sort By"
                 value={
                   filters.sort_by === 'score' ? 'Best Value' :
                   filters.sort_by === 'yield' ? 'Investment Yield (%)' :
                   filters.sort_by === 'price_low' ? 'Price: Low-High' :
                   filters.sort_by === 'price_high' ? 'Price: High-Low' : 'Sort Results'
                 }
                 onChange={(v) => {
                   const mapping: Record<string, any> = {
                     'Best Value': 'score',
                     'Investment Yield (%)': 'yield',
                     'Price: Low-High': 'price_low',
                     'Price: High-Low': 'price_high'
                   };
                   setFilters({...filters, sort_by: mapping[v]});
                 }}
                 icon={Target}
                 type="select"
                 options={filters.listing_type === 'buy' 
                   ? ['Best Value', 'Investment Yield (%)', 'Price: Low-High', 'Price: High-Low']
                   : ['Best Value', 'Price: Low-High', 'Price: High-Low']}
                 className="col-span-2 lg:col-span-1"
               />
            </div>

            {/* 3. ADVANCED FILTERS (EXPANSION) */}
            <AnimatePresence>
             {showAdvanced && (
               <motion.div 
                 ref={advancedRef}
                 initial={{ height: 0, opacity: 0 }}
                 animate={{ height: 'auto', opacity: 1 }}
                 exit={{ height: 0, opacity: 0 }}
                 className="overflow-hidden py-4 border-y border-white/5"
               >
                  <div className="flex flex-col sm:grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                     <PropertyCommandCard title="Amenities" icon={Waves}>
                       <div className="grid grid-cols-2 gap-2 sm:grid-cols-1 sm:gap-2.5">
                         <Toggle label="Swimming Pool" icon={Waves} active={filters.amenities.has_pool} onClick={() => setFilters({...filters, amenities: {...filters.amenities, has_pool: !filters.amenities.has_pool}})} />
                         <Toggle label="Health Club/Gym" icon={Dumbbell} active={filters.amenities.has_gym} onClick={() => setFilters({...filters, amenities: {...filters.amenities, has_gym: !filters.amenities.has_gym}})} />
                         <Toggle label="Gated Community" icon={ShieldCheck} active={filters.amenities.is_gated_community} onClick={() => setFilters({...filters, amenities: {...filters.amenities, is_gated_community: !filters.amenities.is_gated_community}})} />
                         <Toggle label="Power Backup" icon={Zap} active={filters.amenities.has_power_backup} onClick={() => setFilters({...filters, amenities: {...filters.amenities, has_power_backup: !filters.amenities.has_power_backup}})} />
                       </div>
                     </PropertyCommandCard>

                     <PropertyCommandCard title="Location Features" icon={MapPin}>
                       <div className="grid grid-cols-2 gap-2 sm:grid-cols-1 sm:gap-2.5">
                         <Toggle label="Near Metro" icon={TrainFront} active={filters.location_features.is_near_metro} onClick={() => setFilters({...filters, location_features: {...filters.location_features, is_near_metro: !filters.location_features.is_near_metro}})} />
                         <Toggle label="Corner Plot" icon={Split} active={filters.location_features.is_corner_property} onClick={() => setFilters({...filters, location_features: {...filters.location_features, is_corner_property: !filters.location_features.is_corner_property}})} />
                         <Toggle label="Park Facing" icon={Trees} active={filters.location_features.is_park_facing} onClick={() => setFilters({...filters, location_features: {...filters.location_features, is_park_facing: !filters.location_features.is_park_facing}})} />
                         <Toggle label="Vastu Compliant" icon={Compass} active={filters.location_features.is_vastu_compliant} onClick={() => setFilters({...filters, location_features: {...filters.location_features, is_vastu_compliant: !filters.location_features.is_vastu_compliant}})} />
                       </div>
                     </PropertyCommandCard>

                     <PropertyCommandCard title="Asset Specs" icon={LayoutPanelLeft}>
                       <div className="grid grid-cols-2 gap-2 sm:grid-cols-1 sm:gap-2.5">
                         <Toggle label="Luxury Finish" icon={Crown} active={filters.property_features.is_luxury} onClick={() => setFilters({...filters, property_features: {...filters.property_features, is_luxury: !filters.property_features.is_luxury}})} />
                         <Toggle label="Brand New Build" icon={Construction} active={filters.property_features.is_new_construction} onClick={() => setFilters({...filters, property_features: {...filters.property_features, is_new_construction: !filters.property_features.is_new_construction}})} />
                         <Toggle label="Servant Room" icon={UserPlus} active={filters.property_features.is_servant_room} onClick={() => setFilters({...filters, property_features: {...filters.property_features, is_servant_room: !filters.property_features.is_servant_room}})} />
                         <Toggle label="Study/Office" icon={BookOpen} active={filters.property_features.is_study_room} onClick={() => setFilters({...filters, property_features: {...filters.property_features, is_study_room: !filters.property_features.is_study_room}})} />
                       </div>
                     </PropertyCommandCard>
                  </div>
               </motion.div>
             )}
            </AnimatePresence>


            {/* 4. ACTIONS ROW */}
            <div className="pt-4 sm:pt-6">
               <button 
                 onClick={handleDiscover}
                 disabled={loading}
                 className="w-full bg-primary text-black font-black text-xs sm:text-lg uppercase tracking-[0.4em] rounded-xl sm:rounded-2xl h-14 sm:h-24 flex items-center justify-center gap-4 hover:brightness-110 active:scale-[0.98] transition-all shadow-2xl shadow-primary/20 group"
               >
                 {loading ? <Loader2 className="w-5 h-5 sm:w-6 sm:h-6 animate-spin" /> : <Radar className="w-5 h-5 sm:w-6 sm:h-6 group-hover:scale-110 transition-transform duration-500" />}
                 <span className="sm:inline hidden">SEARCH</span>
                 <span className="sm:hidden inline">SEARCH</span>
               </button>
            </div>


        </div>
      </div>

      {/* DISCOVERY RESULTS FEED */}
      <div className="space-y-10 sm:space-y-12">
         <div className="flex flex-col sm:flex-row items-center justify-between gap-6 border-b border-white/5 pb-10 px-1">
            <div className="flex items-center gap-6">
               <div className="flex items-center gap-3">
                  <Target className="w-5 h-5 text-primary" />
                                    <span className="text-[10px] font-black uppercase tracking-[0.4em] text-[#adaaab] blur-[0.2px]">
                    {loading ? 'Fleet Scan in Progress...' : `${results.length} Artifacts Scanned`}
                  </span>
               </div>
            </div>
         </div>

         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-8 items-stretch pt-4 min-h-[400px]">
            <AnimatePresence mode="popLayout">
              {loading ? (
                Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="aspect-[4/5] rounded-[2rem] bg-white/[0.02] border border-white/5 animate-pulse" />
                ))
              ) : results.length > 0 ? (
                results.map((item, i) => (
                  <motion.div
                    key={`${(item as any).society || (item as any).locality}-${i}`}
                    layout
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    transition={{ duration: 0.5, delay: i * 0.05 }}
                  >
                    <PropertyCard 
                      item={item} 
                      intent={filters.listing_type} 
                      onClick={handleCardClick} 
                    />
                  </motion.div>
                ))
              ) : (
                <div className="col-span-full py-32 flex flex-col items-center justify-center space-y-8 text-center">
                   <div className="w-24 h-24 rounded-[2rem] bg-white/[0.02] flex items-center justify-center border border-white/5 shadow-2xl relative">
                      <Sparkles className="w-10 h-10 text-white/5" />
                      <div className="absolute inset-0 bg-primary/5 rounded-[2rem] blur-xl" />
                   </div>
                   <div className="space-y-3">
                      <h4 className="text-2xl font-black font-headline uppercase tracking-tight text-white">No Alpha Signals</h4>
                      <p className="text-sm text-[#adaaab] font-light max-w-sm mx-auto leading-relaxed">
                        Adjust your Tactical Discovery Protocol to expand the market horizon.
                      </p>
                   </div>
                   <button 
                     onClick={() => setFilters({...filters, budget_max: 500000000, city: 'Entire NCR'})}
                     className="px-8 py-3 rounded-xl border border-primary/20 text-primary text-[10px] font-black uppercase tracking-[0.2em] hover:bg-primary/5 transition-all"
                   >
                      Reset Signal Parameters
                   </button>
                </div>
              )}
            </AnimatePresence>
         </div>
      </div>

      <PropertyDeepDive 
        item={selectedItem} 
        isOpen={isDrawerOpen} 
        onClose={() => setIsDrawerOpen(false)}
        intent={filters.listing_type}
      />
    </div>
  );
}
