'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Intent } from '@/types';
import { formatCurrency } from '@/lib/api';
import { MapPin, TrendingUp, ShieldCheck } from 'lucide-react';

interface CardProps {
  item: any;
  intent: Intent;
}

export const PropertyCard: React.FC<CardProps> = ({ item, intent }) => {
  const society = item.society || 'Standard Alpha Unit';
  const locality = item.locality || item.sector || 'NCR Buffer Zone';
  const price = item.price || 0;
  const area = item.area || 0;
  const psqft = item.price_per_sqft || 0;
  const yld = item.yield_pct || 0;
  const score = item.unified_score || 0;
  const bhk = item.bhk || '–';

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="premium-card p-6 sm:p-8 group flex flex-col gap-8 h-full"
    >
      {/* Header: Institutional Density */}
      <div className="flex justify-between items-start gap-4">
        <div className="space-y-2 flex-1">
          <h5 className="font-headline font-black text-2xl text-white group-hover:text-primary transition-colors leading-tight">
            {society}
          </h5>
          <div className="flex items-center gap-2 text-[10px] font-black text-white/40 uppercase tracking-[0.2em]">
            <MapPin className="w-3 h-3 text-primary/60" />
            <span>{locality}, {item.city || 'NCR'}</span>
          </div>
        </div>
        <div className="flex-shrink-0 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[9px] font-black uppercase tracking-widest text-primary">
          {score}/10 RATING
        </div>
      </div>

      {/* Primary Metrics: Atmospheric Display */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white/[0.03] p-5 rounded-2xl flex flex-col gap-2 border border-white/5">
          <p className="text-[9px] font-black text-white/30 uppercase tracking-[0.2em]">{intent === 'Buy' ? 'Asset Value' : 'Monthly Yield'}</p>
          <p className="text-xl font-black font-headline text-white">{formatCurrency(price)}</p>
        </div>
        <div className="bg-white/[0.03] p-5 rounded-2xl flex flex-col gap-2 border border-white/5">
          <p className="text-[9px] font-black text-white/30 uppercase tracking-[0.2em]">Net Coverage</p>
          <p className="text-xl font-black font-headline text-white">{area} <span className="text-[10px] opacity-40">SQFT</span></p>
        </div>
      </div>

      {/* Secondary Intel HUD */}
      <div className="flex items-center justify-between pt-6 border-t border-white/10 mt-auto">
        <div className="flex items-center gap-6">
          <MetricHUD label="₹/SQFT" value={psqft.toLocaleString()} icon={<TrendingUp className="w-3 h-3" />} />
          <div className="w-[1px] h-8 bg-white/10" />
          <MetricHUD 
            label={intent === 'Buy' ? 'EST. YIELD' : 'QUANTUM'} 
            value={intent === 'Buy' ? `${yld}%` : bhk} 
            icon={<ShieldCheck className="w-3 h-3" />}
          />
        </div>
        <div className="h-10 w-10 rounded-full border border-primary/20 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-black transition-all cursor-pointer">
           <TrendingUp className="w-4 h-4" />
        </div>
      </div>
    </motion.div>
  );
};

const MetricHUD = ({ label, value, icon }: any) => (
  <div className="flex flex-col gap-1.5">
    <div className="flex items-center gap-1.5 opacity-30">
      {icon}
      <span className="text-[8px] font-black uppercase tracking-widest">{label}</span>
    </div>
    <span className="text-xs font-black text-white tracking-widest">{value}</span>
  </div>
);
