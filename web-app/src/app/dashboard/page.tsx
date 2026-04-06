'use client';

import React, { useState, useEffect, useCallback, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { predictProperty, getLocalities } from '@/lib/api';
import { PropertyInput, PredictionResponse, PropertyAsset, Recommendation } from '@/types';
import { ValuationHUD } from '@/components/dashboard/ValuationHUD';
import { PropertyDeepDive } from '@/components/dashboard/PropertyDeepDive';
import { 
  Loader2, MapPin, Building, Ruler, Send, Settings2, ChevronDown, Check,
  Waves, Dumbbell, ShieldCheck, Zap, TrainFront, Compass, Trees, 
  Split, Crown, Sparkles, UserPlus, BookOpen, Wifi, Wrench, 
  ArrowUpToLine, LayoutPanelLeft, Box, Archive, Flame, Construction
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

  // Note: 'mounted' check removed to bypass Next.js 16/Turbopack blank-screen hydration trap.
  // if (!mounted) return null;

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-28 pb-12 sm:pt-32 sm:pb-20 lg:pt-36 lg:pb-24 space-y-16" suppressHydrationWarning>
      
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
            Get accurate property valuations for any society in the NCR region.
          </p>
        </div>
      </header>

      {/* COMMAND CENTER */}
      <div className="relative group max-w-5xl mx-auto">
        <div className="absolute -inset-1 bg-gradient-to-r from-primary/5 via-primary/10 to-primary/5 rounded-[2.5rem] blur-2xl opacity-0 group-hover:opacity-100 transition-all duration-1000" />
        
        <div className="relative bg-[#0a0a0a]/80 backdrop-blur-3xl border border-white/5 rounded-2xl sm:rounded-[2rem] lg:rounded-[2.5rem] p-5 sm:p-10 lg:p-12 space-y-10 sm:space-y-12 overflow-hidden">
        
        {/* INTENT SELECTION (TOP LEVEL) */}
        <div className="mb-4 flex justify-start">
           <div className="inline-flex p-1.5 bg-white/[0.02] border border-white/5 rounded-2xl gap-2">
              {['buy', 'rent'].map((t) => (
                <button
                  key={t}
                  onClick={() => setInput({...input, listing_type: t as any})}
                  className={`px-6 sm:px-8 py-2.5 min-h-[44px] rounded-xl text-[10px] font-black uppercase tracking-[0.2em] transition-all duration-300 active:scale-95 ${
                    input.listing_type === t 
                      ? 'bg-primary text-black shadow-[0_0_20px_rgba(189,157,255,0.3)]' 
                      : 'text-[#adaaab] hover:text-white hover:bg-white/5'
                  }`}
                >
                  {t}
                </button>
              ))}
           </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-10 items-start">
           <InputPorter 
             label="NCR City" 
             value={input.city} 
             onChange={(v) => setInput({...input, city: v})} 
             icon={MapPin} 
             type="select"
             options={['Gurgaon', 'Noida', 'Delhi', 'Ghaziabad', 'Faridabad', 'Greater Noida']}
           />
           <InputPorter 
             label="Locality / Sector" 
             value={input.sector} 
             onChange={(v) => setInput({...input, sector: v})} 
             icon={Building} 
             type="select"
             options={localities}
           />
           <InputPorter 
             label="Base BHK" 
             value={input.bedrooms} 
             onChange={(v) => setInput({...input, bedrooms: parseInt(v) || 0})} 
             icon={Ruler} 
             type="number" 
           />
        </div>

        <div className="mt-12 sm:mt-16 pt-12 sm:pt-16 border-t border-white/5 space-y-12">
           
           <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 sm:gap-10">
              <InputPorter 
                label="Target Space (SQFT)"
                value={input.area}
                onChange={(v) => setInput({...input, area: v})}
                icon={Box}
                type="range"
                min={500}
                max={12000}
                step={50}
                placeholder={`Current Metric: ${input.area} Sq.Ft`}
              />
              
              <div className="space-y-4 pt-1.5">
                 <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.3em] text-primary">Asset Type</div>
                 <InstitutionalSelect 
                    value={input.prop_type} 
                    onChange={(v) => setInput({...input, prop_type: v as any})} 
                    options={['Apartment', 'Builder Floor', 'Independent House']}
                 />
              </div>

            </div>

            {/* Advanced Metadata Toggle */}
           <div className="space-y-6">
              <button 
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center gap-3 text-[10px] font-black uppercase tracking-[0.3em] text-white/40 hover:text-primary transition-colors"
              >
                <Settings2 className="w-4 h-4" />
                <span>More Property Details</span>
                <ChevronDown className={`w-4 h-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
              </button>

              <AnimatePresence>
                {showAdvanced && (
                  <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 py-10 border-t border-white/5">
                       {/* CARD 1: AMENITIES & LIFESTYLE */}
                       <PropertyCommandCard title="Amenities & Lifestyle" icon={Waves}>
                          <div className="grid grid-cols-1 gap-3">
                             <Toggle label="Swimming Pool" icon={Waves} active={input.amenities.has_pool} onClick={() => setInput({...input, amenities: {...input.amenities, has_pool: !input.amenities.has_pool}})} />
                             <Toggle label="Health Club/Gym" icon={Dumbbell} active={input.amenities.has_gym} onClick={() => setInput({...input, amenities: {...input.amenities, has_gym: !input.amenities.has_gym}})} />
                             <Toggle label="Gated Community" icon={ShieldCheck} active={input.amenities.is_gated_community} onClick={() => setInput({...input, amenities: {...input.amenities, is_gated_community: !input.amenities.is_gated_community}})} />
                             <Toggle label="Power Backup" icon={Zap} active={input.amenities.has_power_backup} onClick={() => setInput({...input, amenities: {...input.amenities, has_power_backup: !input.amenities.has_power_backup}})} />
                          </div>
                       </PropertyCommandCard>

                       {/* CARD 2: LOCATION HIGHLIGHTS */}
                       <PropertyCommandCard title="Location Highlights" icon={MapPin}>
                          <div className="grid grid-cols-1 gap-3">
                             <Toggle label="Near Metro" icon={TrainFront} active={input.location.is_near_metro} onClick={() => setInput({...input, location: {...input.location, is_near_metro: !input.location.is_near_metro}})} />
                             <Toggle label="Corner Plot" icon={Split} active={input.location.is_corner_property} onClick={() => setInput({...input, location: {...input.location, is_corner_property: !input.location.is_corner_property}})} />
                             <Toggle label="Park Facing" icon={Trees} active={input.location.is_park_facing} onClick={() => setInput({...input, location: {...input.location, is_park_facing: !input.location.is_park_facing}})} />
                             <Toggle label="Vastu Compliant" icon={Compass} active={input.location.is_vastu_compliant} onClick={() => setInput({...input, location: {...input.location, is_vastu_compliant: !input.location.is_vastu_compliant}})} />
                          </div>
                       </PropertyCommandCard>

                       {/* CARD 3: INTERIOR & LAYOUT */}
                       <PropertyCommandCard title="Interior & Layout" icon={LayoutPanelLeft}>
                          <div className="grid grid-cols-1 gap-2">
                             <Toggle label="Luxury Finish" icon={Crown} active={input.property_features.is_luxury} onClick={() => setInput({...input, property_features: {...input.property_features, is_luxury: !input.property_features.is_luxury}})} />
                             <Toggle label="Brand New Build" icon={Construction} active={input.property_features.is_new_construction} onClick={() => setInput({...input, property_features: {...input.property_features, is_new_construction: !input.property_features.is_new_construction}})} />
                             <Toggle label="Servant Room" icon={UserPlus} active={input.property_features.is_servant_room} onClick={() => setInput({...input, property_features: {...input.property_features, is_servant_room: !input.property_features.is_servant_room}})} />
                             <Toggle label="Study/Home Office" icon={BookOpen} active={input.property_features.is_study_room} onClick={() => setInput({...input, property_features: {...input.property_features, is_study_room: !input.property_features.is_study_room}})} />
                             <Toggle label="WiFi Enabled" icon={Wifi} active={input.amenities.has_wifi} onClick={() => setInput({...input, amenities: {...input.amenities, has_wifi: !input.amenities.has_wifi}})} />
                             <Toggle label="High Ceiling" icon={ArrowUpToLine} active={input.amenities.is_high_ceiling} onClick={() => setInput({...input, amenities: {...input.amenities, is_high_ceiling: !input.amenities.is_high_ceiling}})} />
                          </div>
                       </PropertyCommandCard>
                       
                       {/* CARD 4: ASSET SPECIFICATIONS */}
                       <PropertyCommandCard title="Asset Specifications" icon={Box}>
                          <div className="space-y-6">
                             <div className="space-y-3">
                                <div className="text-[10px] font-black uppercase tracking-widest text-[#adaaab]">Orientation</div>
                                <div className="grid grid-cols-4 gap-2">
                                  {['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW'].map(o => (
                                    <button 
                                      key={o}
                                      onClick={() => setInput({...input, orientation: o as any})}
                                      className={`flex items-center justify-center p-2 rounded-lg border text-[9px] font-black tracking-widest transition-all ${input.orientation === o ? 'bg-primary/20 border-primary/40 text-primary shadow-[0_0_10px_rgba(189,157,255,0.2)]' : 'bg-white/5 border-white/5 text-[#adaaab]'}`}
                                    >
                                      {o}
                                    </button>
                                  ))}
                                </div>
                             </div>
                             <div className="space-y-3">
                                <div className="flex justify-between items-center">
                                   <div className="text-[10px] font-black uppercase tracking-widest text-[#adaaab]">Property Age</div>
                                   <div className="text-[10px] font-black text-primary">{input.property_age} Years</div>
                                </div>
                                <input 
                                  type="range" 
                                  min="0" 
                                  max="20" 
                                  value={input.property_age} 
                                  onChange={(e) => setInput({...input, property_age: parseInt(e.target.value)})}
                                  className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-primary" 
                                />
                             </div>
                          </div>
                       </PropertyCommandCard>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
           </div>

           <div className="flex flex-col lg:flex-row items-stretch lg:items-end justify-between gap-10">
              <button 
                onClick={handlePredict}
                disabled={loading}
                className="w-full lg:w-max bg-primary text-black font-black text-[10px] uppercase tracking-widest rounded-xl sm:rounded-2xl h-14 sm:h-16 px-10 flex items-center justify-center gap-4 hover:brightness-110 active:scale-95 transition-all shadow-xl shadow-primary/20 disabled:opacity-50"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <ShieldCheck className="w-5 h-5" />}
                Generate Market Report
              </button>
           </div>
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

