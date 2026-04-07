'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Intent } from '@/types';
import { MapPin, TrendingUp, ShieldCheck, Zap, Layers, Sparkles, ChevronRight, Compass } from 'lucide-react';
import { formatNCRPrice, formatArea } from '@/utils/format';
import Link from 'next/link';

interface CardProps {
  item: any;
  intent: Intent;
  onClick?: (item: any) => void;
   index?: number;
}

const MetricHUD = ({ label, value, icon }: any) => (
  <div className="flex flex-col gap-1.5 shrink-0 min-w-[70px]">
    <div className="flex items-center gap-1.5 opacity-60 text-primary">
      {icon}
      <span className="text-[9px] font-black uppercase tracking-widest leading-none">{label}</span>
    </div>
    <span className="text-[11px] font-black text-white uppercase tracking-wider">{value}</span>
  </div>
);

export const PropertyCard = ({ item, intent, onClick, index }: CardProps) => {
  // Mapping logic: Handle both Listing-level assets and Sector-level recommendations
  const name = item.property_name || item.society || item.locality || 'Precision Asset Unit';
  const location = item.locality || item.sector || 'NCR Hub';
  
  // Advanced Resolution: Resolve basic metrics first to allow cross-calculation
  const psqft = item.price_per_sqft || item.median_price_sqft || 0;
  const yield_pct = item.yield_pct || item.investment_yield || item.expected_yield_pct || 0;
  const area = item.area || 1500;
  const bhk = item.bedrooms || item.bhk || item.prop_bhk || '—';

  // For Rent: If direct data is missing, we intelligently derive it.
  // If psqft < 500, it's definitely Rent/SqFt, not Capital Value/SqFt.
  const calculatedRent = psqft < 500 ? (psqft * area) : ((psqft * area * (yield_pct || 3) / 100) / 12);
  const price = intent === 'buy' 
    ? (item.price || (psqft > 0 ? psqft * area : 0))
    : (item.predicted_monthly_rent || 
       item.monthly_rent || 
       (psqft > 0 ? calculatedRent : 0));
 
  // Deep Dive Link Params
  const deepDiveUrl = `/dashboard?city=${encodeURIComponent(item.city || 'Noida')}&sector=${encodeURIComponent(item.locality || item.sector || '')}&area=${area}&bhk=${bhk}`;
 
  // Advanced Intelligence Metrics
  const score = Number(item.unified_score || item.composite_score || item.deal_score || 0);
  const furnishing = item.furnishing_status || item.furnishing || 'Unfurnished';

  // Dynamic Color Schema for High-Alpha Signals
  const getScoreColor = (s: number) => {
    if (s >= 9) return 'text-[#00FF94] bg-[#00FF94]/10 border-[#00FF94]/20';
    if (s >= 7) return 'text-primary bg-primary/10 border-primary/20';
    return 'text-[#adaaab] bg-white/5 border-white/10';
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.01, boxShadow: '0 0 30px rgba(189,157,255,0.08)' }}
      viewport={{ once: true }}
      onClick={() => onClick?.(item)}
      className="premium-card p-5 sm:p-8 group flex flex-col gap-6 sm:gap-8 cursor-pointer 
                 bg-white/[0.03] sm:bg-transparent sm:hover:bg-white/[0.04] 
                 border border-white/5 sm:border-transparent sm:hover:border-white/10
                 active:scale-[0.98] transition-all relative shadow-2xl sm:shadow-none"
    >
      {/* BACKGROUND DECOR */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 blur-[60px] rounded-full -mr-16 -mt-16 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
      
      {/* Header: Institutional Density */}
      <div className="flex justify-between items-start gap-4 relative z-10 w-full">
        <div className="space-y-1.5 flex-1 min-w-0">
          <div className="flex items-start gap-2">
            {index && (
              <span className="text-[10px] font-black text-primary/40 font-mono tracking-tighter mt-1">
                {index.toString().padStart(2, '0')}.
              </span>
            )}
            <h5 className="font-headline font-black text-[13px] sm:text-base text-white group-hover:text-primary transition-colors leading-tight line-clamp-2 min-h-[3.2rem]">
              {name}
            </h5>
          </div>
          <div className="flex items-center gap-2 text-[10px] font-black text-[#adaaab] uppercase tracking-[0.2em] mb-3">
            <MapPin className="w-3 h-3 text-primary/60" />
            <span className="truncate">{location}, {item.city || 'NCR'}</span>
          </div>

          {/* Contextual Intelligence Tags */}
          <div className="flex flex-wrap gap-2 pt-1">
            {item.dist_to_metro_km && item.dist_to_metro_km < 1.5 && (
              <span className="px-2 py-0.5 rounded-md bg-green-500/10 text-green-400 text-[8px] font-black uppercase tracking-widest border border-green-500/20 flex items-center gap-1">
                <Compass className="w-2.5 h-2.5" /> Metro Link
              </span>
            )}
            {item.features?.amenities?.is_gated_community && (
              <span className="px-2 py-0.5 rounded-md bg-primary/10 text-primary text-[8px] font-black uppercase tracking-widest border border-primary/20 flex items-center gap-1">
                <ShieldCheck className="w-2.5 h-2.5" /> Gated
              </span>
            )}
             {item.features?.property?.is_luxury && (
              <span className="px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-400 text-[8px] font-black uppercase tracking-widest border border-amber-500/20 flex items-center gap-1">
                <Sparkles className="w-2.5 h-2.5" /> Luxury
              </span>
            )}
             {item.features?.amenities?.has_pool && (
              <span className="px-2 py-0.5 rounded-md bg-blue-500/10 text-blue-400 text-[8px] font-black uppercase tracking-widest border border-blue-500/20">
                Pool
              </span>
            )}
          </div>
        </div>
        <div className={`flex-shrink-0 px-3 py-1.5 rounded-lg border text-[9px] font-black uppercase tracking-[0.2em] transition-all duration-500 shadow-lg ${getScoreColor(score)}`}>
           {score > 0 ? `${score % 1 === 0 ? score : score.toFixed(1)} / 10` : 'UNRATED'}
        </div>
      </div>

      {/* Primary Metrics: Atmospheric Display */}
      <div className="grid grid-cols-2 gap-4 relative z-10">
        <div className="bg-white/[0.02] p-5 rounded-2xl flex flex-col gap-2 border border-white/5 group-hover:border-white/10 transition-colors">
          <div className="flex items-center gap-2 opacity-30">
             <Zap className="w-3 h-3" />
             <p className="text-[10px] font-black text-white uppercase tracking-[0.2em]">{intent === 'buy' ? 'Value' : 'Monthly Rent'}</p>
          </div>
          <p className="text-lg sm:text-xl font-black font-headline text-white">{formatNCRPrice(price)}</p>
        </div>
        <div className="bg-white/[0.02] p-5 rounded-2xl flex flex-col gap-2 border border-white/5 group-hover:border-white/10 transition-colors">
          <div className="flex items-center gap-2 opacity-30">
             <Layers className="w-3 h-3" />
             <p className="text-[10px] font-black text-white uppercase tracking-[0.2em]">Area</p>
          </div>
          <p className="text-lg sm:text-xl font-black font-headline text-white">{formatArea(area)}</p>
        </div>
      </div>

      {/* Secondary Intel HUD: Dynamic Density */}
      <div className="flex flex-col gap-6 pt-6 border-t border-white/5 mt-auto relative z-10">
        {/* Metric Grid: High-Value Reading */}
        <div className="grid grid-cols-2 xs:flex xs:items-center gap-y-6 gap-x-8">
           {intent === 'buy' ? (
              <MetricHUD label="₹/SQFT" value={psqft.toLocaleString()} icon={<TrendingUp className="w-3 h-3" />} />
           ) : (
              <MetricHUD label="SECURITY DEP." value={formatNCRPrice(price * 2)} icon={<ShieldCheck className="w-3 h-3" />} />
           )}
           {intent === 'buy' ? (
              <MetricHUD label="EST. YIELD" value={`${yield_pct.toFixed(2)}%`} icon={<ShieldCheck className="w-3 h-3" />} />
           ) : (
              <MetricHUD label="LAYOUT" value={`${bhk} BHK`} icon={<Layers className="w-3 h-3" />} />
           )}
        </div>
        
        {/* REFINED TACTICAL CTA: Persistent High-Alpha Button */}
        <div className="w-full select-none cursor-pointer group/cta">
          <div className="flex items-center justify-between px-4 py-3 bg-primary/10 rounded-xl border border-primary/20 
                        hover:bg-primary/20 hover:border-primary/30 transition-all duration-300">
             <span className="text-[11px] font-black uppercase tracking-[0.2em] text-primary">Institutional Report</span>
             <ChevronRight className="w-4 h-4 text-primary animate-pulse" />
          </div>
        </div>
      </div>
    </motion.div>
  );
};
