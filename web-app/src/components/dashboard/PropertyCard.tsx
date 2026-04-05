'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Intent } from '@/types';
import { MapPin, TrendingUp, ShieldCheck, Zap, Layers, Sparkles, ChevronRight } from 'lucide-react';
import { formatNCRPrice, formatArea } from '@/utils/format';
import Link from 'next/link';

interface CardProps {
  item: any;
  intent: Intent;
  onClick?: (item: any) => void;
  showDeepDive?: boolean;
}

const MetricHUD = ({ label, value, icon }: any) => (
  <div className="flex flex-col gap-1.5">
    <div className="flex items-center gap-1.5 opacity-30">
      {icon}
      <span className="text-[10px] font-black uppercase tracking-widest">{label}</span>
    </div>
    <span className="text-[11px] font-black text-white uppercase tracking-wider">{value}</span>
  </div>
);

export const PropertyCard = ({ item, intent, onClick }: CardProps) => {
  // Mapping logic: Handle both Listing-level assets and Sector-level recommendations
  const name = item.property_name || item.society || item.locality || 'Precision Asset Unit';
  const location = item.locality || item.sector || 'NCR Hub';
  
  // Advanced Resolution: Resolve basic metrics first to allow cross-calculation
  const psqft = item.price_per_sqft || item.median_price_sqft || 0;
  const yield_pct = item.yield_pct || item.investment_yield || item.expected_yield_pct || 0;
  const area = item.area || 1500;
  const bhk = item.bedrooms || item.bhk || item.prop_bhk || '—';

  // Total price resolution (Asset price or calculated from sqft)
  // For Rent: If direct data is missing, we derive the Macro Median using (Price * Yield) / 12
  const price = intent === 'buy' 
    ? (item.price || (psqft > 0 ? psqft * area : 0))
    : (item.predicted_monthly_rent || 
       item.monthly_rent || 
       (psqft > 0 ? (psqft * area * (yield_pct || 3) / 100) / 12 : 0));
 
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
      className="premium-card p-6 sm:p-8 group flex flex-col gap-8 h-full cursor-pointer hover:bg-white/[0.04] active:scale-[0.98] transition-all relative overflow-hidden"
    >
      {/* BACKGROUND DECOR */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 blur-[60px] rounded-full -mr-16 -mt-16 opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
      
      {/* Header: Institutional Density */}
      <div className="flex justify-between items-start gap-4 relative z-10">
        <div className="space-y-2 flex-1">
          <h5 className="font-headline font-black text-xl sm:text-2xl text-white group-hover:text-primary transition-colors leading-tight line-clamp-2">
            {name}
          </h5>
          <div className="flex items-center gap-2 text-[10px] font-black text-[#adaaab] uppercase tracking-[0.2em]">
            <MapPin className="w-3 h-3 text-primary/60" />
            <span className="truncate">{location}, {item.city || 'NCR'}</span>
          </div>
        </div>
        <div className={`flex-shrink-0 px-4 py-2 rounded-xl border text-[10px] font-black uppercase tracking-widest transition-all duration-500 shadow-lg ${getScoreColor(score)}`}>
           {score > 0 ? `${score.toFixed(1)}/10 SCORE` : 'UNRATED'}
        </div>
      </div>

      {/* Primary Metrics: Atmospheric Display */}
      <div className="grid grid-cols-2 gap-4 relative z-10">
        <div className="bg-white/[0.02] p-5 rounded-2xl flex flex-col gap-2 border border-white/5 group-hover:border-white/10 transition-colors">
          <div className="flex items-center gap-2 opacity-30">
             <Zap className="w-3 h-3" />
             <p className="text-[10px] font-black text-white uppercase tracking-[0.2em]">{intent === 'buy' ? 'Market Value' : 'Monthly Rent'}</p>
          </div>
          <p className="text-xl font-black font-headline text-white">{formatNCRPrice(price)}</p>
        </div>
        <div className="bg-white/[0.02] p-5 rounded-2xl flex flex-col gap-2 border border-white/5 group-hover:border-white/10 transition-colors">
          <div className="flex items-center gap-2 opacity-30">
             <Layers className="w-3 h-3" />
             <p className="text-[10px] font-black text-white uppercase tracking-[0.2em]">Asset Area</p>
          </div>
          <p className="text-xl font-black font-headline text-white">{formatArea(area)}</p>
        </div>
      </div>

      {/* Secondary Intel HUD */}
      <div className="flex items-center justify-between pt-6 border-t border-white/5 mt-auto relative z-10">
        <div className="flex items-center gap-6">
          <MetricHUD label="₹/SQFT" value={psqft.toLocaleString()} icon={<TrendingUp className="w-3 h-3" />} />
          <div className="w-[1px] h-8 bg-white/10" />
          <MetricHUD 
            label={intent === 'buy' ? 'EST. YIELD' : 'BHK COUNT'} 
            value={intent === 'buy' ? `${yield_pct.toFixed(2)}%` : `${bhk} BHK`} 
            icon={<ShieldCheck className="w-3 h-3" />}
          />
          {intent === 'rent' && (
            <>
              <div className="w-[1px] h-8 bg-white/10 hidden sm:block" />
              <div className="hidden sm:block">
                <MetricHUD label="FURNISHING" value={furnishing.replace('-', ' ')} icon={<Sparkles className="w-3 h-3" />} />
              </div>
            </>
          )}
        </div>
        
        {/* REFINED TACTICAL CTA: Unlocks on Hover */}
        <div className="flex items-center gap-2 text-[9px] font-black uppercase tracking-widest text-primary opacity-0 group-hover:opacity-100 translate-x-4 group-hover:translate-x-0 transition-all duration-500">
           <span>View Report</span>
           <ChevronRight className="w-3.5 h-3.5" />
        </div>
      </div>
    </motion.div>
  );
};
