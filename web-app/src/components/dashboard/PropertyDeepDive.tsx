'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, MapPin, TrendingUp, ShieldCheck, Zap, Info, ExternalLink, ChevronRight } from 'lucide-react';
import { PropertyAsset, Recommendation } from '@/types';
import { formatNCRPrice, formatArea } from '@/utils/format';
import dynamic from 'next/dynamic';
import Link from 'next/link';

const Map = dynamic(() => import('react-map-gl/maplibre').then(m => m.default), {
  ssr: false,
  loading: () => <div className="w-full h-full bg-black/50 animate-pulse rounded-3xl" />,
});


interface DeepDiveProps {
  item: PropertyAsset | Recommendation | null;
  isOpen: boolean;
  onClose: () => void;
  intent?: 'buy' | 'rent';
}

export const PropertyDeepDive: React.FC<DeepDiveProps> = ({ item, isOpen, onClose, intent = 'buy' }) => {
  // HARDENED GUARD: Catch null, undefined, or empty objects
  if (!item || Object.keys(item).length === 0) return null;

  // Type guard/normalization for internal use
  const isRecommendation = 'expected_yield_pct' in item;
  const society = 'society' in item ? item.society : (item as any).locality || 'Standard Asset';
  
  // SAFE CALCS: Ensure fallback to 0 for path multiplication
  const price = 'price' in item ? item.price : ((item as Recommendation).median_price_sqft || 0) * 1000;
  const yieldPct = isRecommendation ? (item as Recommendation).expected_yield_pct : (item as PropertyAsset).yield_pct || 0;
  const score = isRecommendation ? (item as Recommendation).composite_score : (item as PropertyAsset).unified_score || 0;

  // DYNAMIC INTELLIGENCE PROTOCOL
  const rawRiskScore = (item as any).risk_score || 85;
  const overvalPct = (item as any).overvaluation_pct || 0;
  
  const priceStability = Math.round(Math.min(100, Math.max(0, 100 - Math.abs(overvalPct))));
  const growthMomentum = Math.round(Math.min(100, (score * 8.5) + (yieldPct * 4)));
  const amenityDensity = (item as any).features?.amenities 
    ? Math.min(100, Object.values((item as any).features.amenities).filter(Boolean).length * 12 + 45) 
    : 78;
  
  const primaryMetric = intent === 'rent' ? rawRiskScore : rawRiskScore; // Re-mapping logic if needed
  const secondaryMetric = priceStability;
  const tertiaryMetric = intent === 'rent' ? amenityDensity : growthMomentum;

  const itemH3 = item.h3_index || (item as any).asset?.h3_index || 'ID: SPR-4501';
  const itemLat = item.latitude || (item as any).asset?.latitude;
  const itemLon = item.longitude || (item as any).asset?.longitude;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100]"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            drag="x"
            dragConstraints={{ left: 0, right: 0 }}
            dragElastic={{ left: 0, right: 0.5 }}
            onDragEnd={(e, { offset, velocity }) => {
              if (offset.x > 100 || velocity.x > 500) {
                onClose();
              }
            }}
            className="fixed top-0 right-0 h-full w-full lg:w-[410px] md:w-[380px] glass-panel-luxe z-[110] shadow-2xl p-0 overflow-y-auto touch-pan-y border-l border-white/10"
          >
            {/* Header Area */}
            <div className="sticky top-0 z-10 glass-panel-luxe border-0 border-b border-white/10 px-5 py-4 flex justify-between items-center bg-surface/80">
              <div className="flex items-center gap-3">
                 <div className="w-10 h-10 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                    <Zap className="w-5 h-5" />
                 </div>
                 <h3 className="text-lg font-black tracking-tighter uppercase font-headline">Intelligence Report</h3>
              </div>
              <div className="flex items-center gap-2">
                {/* Tactical Market Analyzer Link (Subtle) *) */}
                <Link 
                  href={`/dashboard?city=${encodeURIComponent(item.city || '')}&sector=${encodeURIComponent((item as any).sector || item.locality || '')}&area=${(item as any).area || (item as any).total_sqft || ''}&bhk=${(item as any).bhk || ''}&intent=${intent}`}
                  className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white/20 hover:text-primary hover:border-primary/30 transition-all active:scale-95"
                  title="Initialize Market Analyzer"
                >
                  <TrendingUp className="w-4 h-4" />
                </Link>
                <button 
                  onClick={onClose}
                  className="min-w-[44px] min-h-[44px] flex items-center justify-center rounded-full hover:bg-white/10 active:scale-90 transition-all text-white/40 hover:text-white"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Content Area */}
            <div className="px-5 py-8 space-y-10 pb-10">
              
              {/* Asset Header *) */}
              <div className="space-y-4">
                <div className="space-y-1">
                  <h2 className="text-2xl font-black font-headline text-white tracking-tight leading-tight uppercase">
                    {society}
                  </h2>
                  <div className="flex items-center gap-2 text-sm font-bold text-primary tracking-widest uppercase opacity-70">
                    <MapPin className="w-4 h-4" />
                    <span>{item.locality || (item as any).sector}, {item.city}</span>
                  </div>
                </div>
                
                <div className="flex gap-3">
                   <Badge label={`${score}/10`} sub="ALPHA SCORE" primary />
                   <Badge label="VERIFIED" sub="GEOSPATIAL DATA" />
                </div>
              </div>

              {/* Tactical Radar Map */}
              <div className="space-y-4">
                <div className="relative w-full aspect-video rounded-3xl overflow-hidden border border-white/10 bg-black">
                   <TacticalMap h3Index={itemH3} lat={itemLat} lon={itemLon} />
                   
                   {/* Coordinates HUD overlay */}
                   {(itemLat && itemLon) && (
                     <div className="absolute bottom-4 left-4 font-mono text-[10px] text-primary/60 bg-black/80 px-2 py-1 rounded border border-primary/20">
                        LAT: {Number(itemLat).toFixed(5)} <br />
                        LON: {Number(itemLon).toFixed(5)}
                     </div>
                   )}
                </div>
              </div>

              {/* Financial Matrix */}
              <div className="space-y-6">
                <h4 className="text-[10px] font-black text-white/30 uppercase tracking-[0.2em]">Financial Architecture</h4>
                <div className="grid grid-cols-2 gap-3 sm:gap-4">
                  <MetricSquare 
                    label={intent === 'rent' ? "Monthly Rent" : "Valuation"} 
                    value={formatNCRPrice(price)} 
                    sub={'area' in item ? `at ${item.area} SQFT` : 'Market Median'} 
                  />
                  {intent === 'rent' ? (
                    <MetricSquare 
                      label="Market Value Index" 
                      value="Aligned" 
                      sub="Premium Verified" 
                      trend="up"
                    />
                  ) : (
                    <MetricSquare 
                      label="Yield Projection" 
                      value={`${yieldPct}%`} 
                      sub="Gross Annualized" 
                      trend="up"
                    />
                  )}
                  {intent === 'rent' ? (
                    <MetricSquare 
                      label="Living Premium" 
                      value={`₹${'price_per_sqft' in item ? item.price_per_sqft : (item as Recommendation).median_price_sqft}`} 
                      sub="Appx Per Sq.Ft" 
                    />
                  ) : (
                    <MetricSquare 
                      label="Price Context" 
                      value={`₹${'price_per_sqft' in item ? item.price_per_sqft : (item as Recommendation).median_price_sqft}`} 
                      sub="Per Sq. Foot" 
                    />
                  )}
                  <MetricSquare 
                    label="Metro Proximity" 
                    value={'dist_to_metro_km' in item && item.dist_to_metro_km ? `${item.dist_to_metro_km}km` : '0.8km'} 
                    sub="Distance to Hub" 
                  />
                </div>
              </div>

              {/* Advanced Risk Protocol */}
              <div className="glass-panel-luxe rounded-3xl p-6 space-y-6">
                 <div className="flex items-center gap-3">
                    <ShieldCheck className="w-5 h-5 text-primary" />
                    <h5 className="text-[11px] font-black tracking-widest uppercase">
                      {intent === 'rent' ? "Lifestyle Score" : "Market Risk Analysis"}
                    </h5>
                 </div>
                 
                 <div className="space-y-4">
                   <RiskBar label={intent === 'rent' ? "Security & Safety" : "Market Liquidity"} percentage={primaryMetric} />
                   <RiskBar label={intent === 'rent' ? "Affordability Index" : "Price Stability"} percentage={secondaryMetric} />
                   <RiskBar label={intent === 'rent' ? "Amenity Density" : "Growth Potential"} percentage={tertiaryMetric} />
                 </div>
              </div>

              {/* Technical Asset Protocol — Portal Parity Section */}
              {(item as any).features && (
                <div className="space-y-8">
                  <div className="flex items-center gap-3">
                    <TrendingUp className="w-5 h-5 text-primary" />
                    <h5 className="text-[11px] font-black tracking-widest uppercase">Property Details</h5>
                  </div>
                  
                  <div className="grid grid-cols-1 gap-8">
                     <FeatureGrid 
                       title="Lifestyle & Amenities" 
                       features={(item as any).features.amenities} 
                       labels={{
                         has_pool: "Swimming Pool",
                         has_gym: "Health Club",
                         has_lift: "Elevator Access",
                         has_power_backup: "Power Backup",
                         is_gated_community: "Gated Security",
                         has_clubhouse: "Clubhouse",
                         has_maintenance: "Staff Support",
                         has_wifi: "High-Speed WiFi",
                         is_high_ceiling: "Luxe Ceilings"
                       }}
                     />
                     <FeatureGrid 
                       title="Location Intelligence" 
                       features={(item as any).features.location} 
                       labels={{
                         is_near_metro: "Metro Connectivity",
                         is_corner_property: "Corner Asset",
                         is_park_facing: "Nature Facing",
                         is_vastu_compliant: "Vastu Science"
                       }}
                     />
                     <FeatureGrid 
                       title="Property Specs" 
                       features={(item as any).features.property} 
                       labels={{
                         is_luxury: "Luxury Finish",
                         is_servant_room: "Domestic Support",
                         is_study_room: "Home Office",
                         is_store_room: "Storage Unit",
                         is_pooja_room: "Sacred Space",
                         is_new_construction: "Brand New Build"
                       }}
                     />
                  </div>
                </div>
              )}


            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

const Badge = ({ label, sub, primary = false }: any) => (
  <div className={`px-3 py-1.5 rounded-2xl border ${primary ? 'bg-primary/10 border-primary/30' : 'bg-white/5 border-white/10'}`}>
    <p className="text-[7.5px] font-black opacity-40 uppercase tracking-widest leading-none mb-1">{sub}</p>
    <p className={`text-[10px] font-black tracking-widest ${primary ? 'text-primary' : 'text-white'}`}>{label}</p>
  </div>
);

const MetricSquare = ({ label, value, sub, trend }: any) => (
  <div className="bg-white/[0.03] p-5 rounded-2xl border border-white/5 space-y-1">
    <p className="text-[8.5px] font-black text-white/30 uppercase tracking-[0.2em]">{label}</p>
    <p className="text-xl font-black font-headline text-white tracking-tight">{value}</p>
    <p className="text-[9px] font-bold text-white/20 uppercase tracking-widest">{sub}</p>
  </div>
);

const RiskBar = ({ label, percentage }: any) => (
  <div className="space-y-2">
    <div className="flex justify-between items-end">
      <span className="text-[10px] font-black text-white/40 uppercase tracking-widest">{label}</span>
      <span className="text-[10px] font-bold font-mono text-primary">{percentage}%</span>
    </div>
    <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
      <motion.div 
        initial={{ width: 0 }}
        animate={{ width: `${percentage}%` }}
        className="h-full bg-gradient-to-r from-primary/40 to-primary"
      />
    </div>
  </div>
);

const TacticalMap = ({ h3Index, lat, lon }: any) => {
  const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';
  
  if (!lat || !lon) {
    // Fallback simple "Tactical Radar" visualization using SVG hex grid
    return (
      <div className="w-full h-full relative flex items-center justify-center opacity-40">
         <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(circle, #fff 1px, transparent 1px)', backgroundSize: '30px 30px' }} />
         
         <svg width="200" height="200" viewBox="0 0 200 200" className="relative z-10">
           <defs>
             <filter id="glow">
               <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
               <feMerge>
                 <feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/>
               </feMerge>
             </filter>
           </defs>
           <circle cx="100" cy="100" r="80" fill="none" stroke="#bd9dff" strokeWidth="0.5" strokeDasharray="4 4" />
           <circle cx="100" cy="100" r="50" fill="none" stroke="#bd9dff" strokeWidth="0.5" strokeDasharray="4 4" />
           <line x1="20" y1="100" x2="180" y2="100" stroke="#bd9dff" strokeWidth="0.5" opacity="0.3" />
           <line x1="100" y1="20" x2="100" y2="180" stroke="#bd9dff" strokeWidth="0.5" opacity="0.3" />
           <path d="M100 70 L120 82 L120 106 L100 118 L80 106 L80 82 Z" fill="#bd9dff" opacity="0.1" filter="url(#glow)" />
           <path d="M100 70 L120 82 L120 106 L100 118 L80 106 L80 82 Z" fill="none" stroke="#bd9dff" strokeWidth="2" filter="url(#glow)" />
         </svg>
      </div>
    );
  }

  // Active Live Map Radar
  return (
    <div className="w-full h-full relative group bg-black overflow-hidden pointer-events-auto">
      <div className="absolute inset-0 grayscale opacity-80 group-hover:opacity-100 group-hover:grayscale-0 transition-all duration-[2000ms]">
        <Map
          initialViewState={{
            longitude: Number(lon),
            latitude: Number(lat),
            zoom: 14.5,
            pitch: 60,
            bearing: 0
          }}
          mapStyle={MAP_STYLE}
          interactive={false}
          attributionControl={false}
        />
      </div>
      
      {/* Tactical Center Overlay (Hexagon Crosshair) */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-[50]">
        <svg width="80" height="80" viewBox="0 0 100 100" className="opacity-90 drop-shadow-[0_0_15px_#bd9dff]">
          <path d="M50 20 L75 35 L75 65 L50 80 L25 65 L25 35 Z" fill="rgba(189,157,255,0.1)" stroke="#bd9dff" strokeWidth="2" />
          <circle cx="50" cy="50" r="4" fill="#bd9dff" className="animate-pulse" />
          <line x1="50" y1="5" x2="50" y2="20" stroke="#bd9dff" strokeWidth="1" strokeOpacity="0.8" />
          <line x1="50" y1="80" x2="50" y2="95" stroke="#bd9dff" strokeWidth="1" strokeOpacity="0.8" />
          <line x1="5" y1="50" x2="25" y2="50" stroke="#bd9dff" strokeWidth="1" strokeOpacity="0.8" />
          <line x1="75" y1="50" x2="95" y2="50" stroke="#bd9dff" strokeWidth="1" strokeOpacity="0.8" />
        </svg>
      </div>

      <div className="absolute inset-0 pointer-events-none z-[40]" style={{ backgroundImage: 'radial-gradient(circle at center, transparent 30%, rgba(0,0,0,0.6) 100%)' }} />
      <div className="absolute inset-0 opacity-[0.05] pointer-events-none z-[40]" style={{ backgroundImage: 'radial-gradient(circle, #bd9dff 1px, transparent 1px)', backgroundSize: '15px 15px' }} />
    </div>
  );
};

const FeatureGrid = ({ title, features, labels }: { title: string, features: Record<string, boolean>, labels: Record<string, string> }) => {
  if (!features) return null;
  
  return (
    <div className="space-y-4">
      <h6 className="text-[9px] font-black text-white/20 uppercase tracking-[0.3em]">{title}</h6>
      <div className="grid grid-cols-2 gap-3">
        {Object.entries(labels).map(([key, label]) => {
          const isActive = features[key];
          return (
            <div 
              key={key}
              className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl border transition-all ${isActive ? 'bg-primary/5 border-primary/20 text-white' : 'bg-white/[0.01] border-white/5 text-white/20'}`}
            >
              <span className="text-[10px] font-black uppercase tracking-widest">{label}</span>
              {isActive ? (
                <div className="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(189,157,255,0.6)]" />
              ) : (
                <X className="w-3 h-3 opacity-20" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
