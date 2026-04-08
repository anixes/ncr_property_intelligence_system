'use client';


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
  const [localities, setLocalities] = useState<string[]>([]);
  const [mounted, setMounted] = useState(false);

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
              label="Locality / Sector"
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

export default function DashboardView() {
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
