'use client';

export const dynamic = 'force-dynamic';

import React, { useState, useEffect, useCallback, Suspense, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import { predictProperty, getLocalities } from '@/lib/api';
import { PropertyInput, PredictionResponse, PropertyAsset, Recommendation } from '@/types';
import { ValuationHUD } from '@/components/dashboard/ValuationHUD';
import { PropertyDeepDive } from '@/components/dashboard/PropertyDeepDive';
import { 
  Loader2, MapPin, Building, Ruler, Send, Settings2, ChevronDown, Check,
  Waves, Dumbbell, ShieldCheck, Zap, TrainFront, Compass, Trees, 
  Split, Crown, Sparkles, UserPlus, BookOpen, Wifi, Wrench, 
  ArrowUpToLine, LayoutPanelLeft, Box, Archive, Flame, Construction, Target
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { InstitutionalSelect } from '@/components/dashboard/InstitutionalSelect';
import { InputPorter, Toggle, PropertyCommandCard } from '@/components/dashboard/PortalUI';

function DashboardContent() {
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [localities, setLocalities] = useState<string[]>([]);
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
    
    // Deep Linking Pre-fill Logic
    const city = searchParams.get('city');
    const sector = searchParams.get('sector');
    const project = searchParams.get('project');
    const area = searchParams.get('area');
    const bhk = searchParams.get('bhk');
    const intent = searchParams.get('intent') || searchParams.get('listing_type');

    if (city || sector || project || area || bhk || intent) {
      setInput(prev => ({
        ...prev,
        city: city || prev.city,
        sector: sector || prev.sector,
        property_name: project || prev.property_name,
        area: area ? parseInt(area) : prev.area,
        bedrooms: bhk ? parseInt(bhk) : prev.bedrooms,
        listing_type: (intent as any) || prev.listing_type
      }));
    }
  }, [searchParams]);
  
  // Detail Drawer State
  const [selectedItem, setSelectedItem] = useState<PropertyAsset | Recommendation | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const [input, setInput] = useState<PropertyInput>({
    city: 'Noida',
    sector: 'Sector 150',
    property_name: '',
    bedrooms: 3,
    area: 1800,
    prop_type: 'Apartment',
    furnishing_status: 'Semi-Furnished',
    legal_status: 'Freehold',
    listing_type: 'buy',
    amenities: {
      has_pool: false,
      has_gym: false,
      has_lift: true,
      has_power_backup: true,
      is_gated_community: true,
      has_clubhouse: false,
      has_maintenance: false,
      has_wifi: false,
      is_high_ceiling: false
    },
    location: {
      is_near_metro: false,
      is_corner_property: false,
      is_park_facing: false,
      is_vastu_compliant: false
    },
    property_features: {
      is_luxury: false,
      is_servant_room: false,
      is_study_room: false,
      is_store_room: false,
      is_pooja_room: false,
      is_new_construction: false
    },
    is_rera_registered: true,
    no_brokerage: false,
    bachelors_allowed: false,
    is_standalone: false,
    is_owner_listing: false,
    orientation: 'N',
    property_age: 0
  });

  useEffect(() => {
    getLocalities(input.city)
      .then((data) => {
        setLocalities(data);
        // Reset sector if not in new city localities
        if (data.length > 0 && !data.includes(input.sector)) {
          setInput(prev => ({ ...prev, sector: data[0] }));
        }
      })
      .catch(() => {
        console.error('Locality Recovery Failed — using core sectors as fallback.');
        setLocalities(['Sector 150', 'Sector 62', 'Sector 18', 'Sector 128']); 
      });
  }, [input.city]);

  const handlePredict = async () => {
    setLoading(true);
    try {
      const data = await predictProperty(input);
      
      if (!data || typeof data !== "object") {
        throw new Error("Invalid API response shape");
      }

      setResult(data);
      
      // Safe Scroll Delay
      setTimeout(() => {
        document.getElementById('valuation-results')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (error) {
      console.error('Valuation IQ Error:', error);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleCardClick = useCallback((item: any) => {
    setSelectedItem(item);
    setIsDrawerOpen(true);
  }, []);

  // Contextual Auto-fetch when Intent (Buy/Rent) changes after a successful scan
  useEffect(() => {
    // Only auto-fetch if we have already calculated a result previously
    if (mounted && result) {
      handlePredict();
    }
  }, [input.listing_type]);

  return (
    <div className="w-full max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 pt-28 pb-12 sm:pt-32 sm:pb-20 lg:pt-36 lg:pb-24 space-y-16" suppressHydrationWarning>
      
      {/* HEADER PORTER */}
      <header className="space-y-6 sm:space-y-8">
        <div className="inline-flex items-center gap-3 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-[10px] font-black uppercase tracking-[0.4em] border border-primary/10 font-body">
           Property Value Guide
        </div>
        <div className="space-y-4">
          <h1 className="text-3xl sm:text-5xl lg:text-8xl font-black font-headline tracking-tightest leading-[0.85] text-white">
             Market <br className="hidden sm:block"/>
             <span className="text-[#adaaab]">Analyzer.</span>
          </h1>
          <p className="text-base sm:text-lg md:text-2xl text-[#adaaab] font-light max-w-2xl leading-relaxed tracking-tight font-body italic">
            Instantly estimate the true market value of any sector or locality in the NCR region using our machine learning model.
          </p>
        </div>
      </header>

      {/* COMMAND CENTER */}
      <div className="relative group max-w-5xl mx-auto">
        <div className="absolute -inset-1 bg-gradient-to-r from-primary/5 via-primary/10 to-primary/5 rounded-[2.5rem] blur-2xl opacity-0 group-hover:opacity-100 transition-all duration-1000" />
        
        <div className="relative bg-[#0a0a0a]/80 backdrop-blur-3xl border border-white/5 rounded-2xl sm:rounded-[2rem] lg:rounded-[2.5rem] p-4 sm:p-10 lg:p-12 space-y-6 sm:space-y-8 overflow-hidden">
        
         {/* 1. INTENT & ADVANCED TOGGLE ROW */}
         <div className="flex items-center justify-between gap-4">
            <div className="inline-flex p-1 bg-white/[0.02] border border-white/5 rounded-xl gap-1">
                {['buy', 'rent'].map((t) => (
                  <button
                    key={t}
                    onClick={() => setInput({...input, listing_type: t as any})}
                    className={`px-5 sm:px-8 py-2 rounded-lg text-[9px] font-black uppercase tracking-[0.1em] transition-all duration-300 active:scale-95 ${
                      input.listing_type === t 
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
              value={input.city}
              onChange={(v) => setInput({...input, city: v})}
              icon={MapPin}
              type="select"
              options={['Gurgaon', 'Noida', 'Delhi', 'Ghaziabad', 'Faridabad']}
              className="col-span-1"
            />
            
            <InputPorter 
              label="Sector"
              value={input.sector}
              onChange={(v) => setInput({...input, sector: v})}
              icon={Target}
              type="select"
              options={localities}
              placeholder="e.g. Sector 150"
              className="col-span-1"
            />

            <InputPorter 
              label="Prop Type"
              value={input.prop_type}
              onChange={(v) => setInput({...input, prop_type: v})}
              icon={Building}
              type="select"
              options={['Apartment', 'Builder Floor', 'Independent House']}
              className="col-span-2 lg:col-span-1"
            />

            <InputPorter 
              label="BHK"
              value={input.bedrooms}
              onChange={(v) => setInput({...input, bedrooms: Number(v)})}
              icon={Split}
              type="range"
              min={1}
              max={5}
              step={1}
              placeholder="1-5 BHK"
              className="col-span-1 sm:col-span-2 lg:col-span-1"
            />

            <InputPorter 
              label="Area (SqFt)"
              value={input.area}
              onChange={(v) => setInput({...input, area: v})}
              icon={Ruler}
              type="range"
              min={100}
              max={10000}
              step={100}
              placeholder="1800 SqFt"
              className="col-span-1 sm:col-span-2 lg:col-span-2"
            />
         </div>

         {/* 4. ADVANCED FILTERS (EXPANSION) */}
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
                      <Toggle label="Swimming Pool" icon={Waves} active={input.amenities.has_pool} onClick={() => setInput({...input, amenities: {...input.amenities, has_pool: !input.amenities.has_pool}})} />
                      <Toggle label="Health Club/Gym" icon={Dumbbell} active={input.amenities.has_gym} onClick={() => setInput({...input, amenities: {...input.amenities, has_gym: !input.amenities.has_gym}})} />
                      <Toggle label="Gated Community" icon={ShieldCheck} active={input.amenities.is_gated_community} onClick={() => setInput({...input, amenities: {...input.amenities, is_gated_community: !input.amenities.is_gated_community}})} />
                      <Toggle label="Power Backup" icon={Zap} active={input.amenities.has_power_backup} onClick={() => setInput({...input, amenities: {...input.amenities, has_power_backup: !input.amenities.has_power_backup}})} />
                    </div>
                  </PropertyCommandCard>

                  <PropertyCommandCard title="Location Features" icon={MapPin}>
                    <div className="grid grid-cols-2 gap-2 sm:grid-cols-1 sm:gap-2.5">
                      <Toggle label="Near Metro" icon={TrainFront} active={input.location.is_near_metro} onClick={() => setInput({...input, location: {...input.location, is_near_metro: !input.location.is_near_metro}})} />
                      <Toggle label="Corner Plot" icon={Split} active={input.location.is_corner_property} onClick={() => setInput({...input, location: {...input.location, is_corner_property: !input.location.is_corner_property}})} />
                      <Toggle label="Park Facing" icon={Trees} active={input.location.is_park_facing} onClick={() => setInput({...input, location: {...input.location, is_park_facing: !input.location.is_park_facing}})} />
                      <Toggle label="Vastu Compliant" icon={Compass} active={input.location.is_vastu_compliant} onClick={() => setInput({...input, location: {...input.location, is_vastu_compliant: !input.location.is_vastu_compliant}})} />
                    </div>
                  </PropertyCommandCard>

                  <PropertyCommandCard title="Asset Specs" icon={LayoutPanelLeft}>
                    <div className="space-y-6">
                        <div className="grid grid-cols-2 gap-2 sm:grid-cols-1 sm:gap-2.5">
                             <Toggle label="Luxury Finish" icon={Crown} active={input.property_features.is_luxury} onClick={() => setInput({...input, property_features: {...input.property_features, is_luxury: !input.property_features.is_luxury}})} />
                             <Toggle label="Brand New Build" icon={Construction} active={input.property_features.is_new_construction} onClick={() => setInput({...input, property_features: {...input.property_features, is_new_construction: !input.property_features.is_new_construction}})} />
                             <Toggle label="Servant Room" icon={UserPlus} active={input.property_features.is_servant_room} onClick={() => setInput({...input, property_features: {...input.property_features, is_servant_room: !input.property_features.is_servant_room}})} />
                             <Toggle label="Study/Office" icon={BookOpen} active={input.property_features.is_study_room} onClick={() => setInput({...input, property_features: {...input.property_features, is_study_room: !input.property_features.is_study_room}})} />
                        </div>
                        
                        {/* SECONDARY SPECS */}
                        <div className="space-y-4 pt-2 border-t border-white/5">
                          <div className="space-y-2">
                             <label className="text-[10px] font-black uppercase tracking-widest text-[#adaaab]">Furnishing Status</label>
                             <div className="grid grid-cols-3 gap-2">
                               {['Unfurnished', 'Semi-Furnished', 'Furnished'].map(o => (
                                 <button 
                                   key={o} onClick={() => setInput({...input, furnishing_status: o as any})}
                                   className={`px-2 py-1.5 rounded-lg text-[8px] font-bold uppercase tracking-tight transition-all ${input.furnishing_status === o ? 'bg-primary/20 text-primary border border-primary/20' : 'bg-white/[0.02] text-[#adaaab] border border-white/5'}`}
                                 >
                                   {o}
                                 </button>
                               ))}
                             </div>
                          </div>
                           <InputPorter 
                             label="Age"
                             value={input.property_age}
                             onChange={(v) => setInput({...input, property_age: v})}
                             type="range"
                             min={0}
                             max={20}
                             step={1}
                             placeholder="New - 20Y"
                           />
                        </div>
                    </div>
                  </PropertyCommandCard>
               </div>
            </motion.div>
          )}
         </AnimatePresence>

         {/* 5. ACTION ROW */}
         <div className="pt-4 pb-2">
            <button 
              onClick={handlePredict}
              disabled={loading}
              className="w-full bg-primary text-black font-black text-xs sm:text-sm uppercase tracking-[0.3em] rounded-xl sm:rounded-2xl h-16 sm:h-20 flex items-center justify-center gap-4 hover:brightness-110 active:scale-95 transition-all shadow-xl shadow-primary/20 disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <ShieldCheck className="w-5 h-5" />}
              SCAN
            </button>
         </div>
        </div>
      </div>

      <div id="valuation-results">
        {result && (
          <ValuationHUD 
            data={result} 
            intent={input.listing_type as any} 
            onCardClick={handleCardClick} 
          />
        )}
      </div>

      {selectedItem && (
        <PropertyDeepDive 
          item={selectedItem} 
          isOpen={isDrawerOpen} 
          onClose={() => setIsDrawerOpen(false)} 
          intent={input.listing_type as any}
        />
      )}
    </div>
  );
}

export default function Dashboard() {
  return (
    <Suspense fallback={
      <div className="w-full h-screen flex items-center justify-center bg-[#0a0a0a]">
        <div className="w-8 h-8 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
      </div>
    }>
      <DashboardContent />
    </Suspense>
  );
}
