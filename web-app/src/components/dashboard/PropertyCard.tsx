'use client';

import React from 'react';
import { Intent } from '@/types';
import { formatCurrency } from '@/lib/api';

interface CardProps {
  item: any;
  intent: Intent;
}

export const PropertyCard: React.FC<CardProps> = ({ item, intent }) => {
  const society = item.society || 'Unknown';
  const locality = item.locality || item.sector || '';
  const price = item.price || 0;
  const area = item.area || 0;
  const psqft = item.price_per_sqft || 0;
  const yld = item.yield_pct || 0;
  const score = item.unified_score || 0;
  const bhk = item.bhk || '–';

  return (
    <div className="premium-card p-5 group flex flex-col gap-4">
      <div className="space-y-1">
        <h5 className="font-black text-lg text-white/90 truncate">{society}</h5>
        <p className="text-[10px] font-bold text-white/30 uppercase tracking-widest">{locality}, {item.city}</p>
      </div>

      <div className="grid grid-cols-3 gap-2">
        <div className="bg-white/5 p-3 rounded-xl flex flex-col gap-1">
          <p className="text-[8px] font-bold opacity-30 uppercase">{intent === 'Buy' ? 'Price' : 'Rent'}</p>
          <p className="text-xs font-black">{formatCurrency(price)}</p>
        </div>
        <div className="bg-white/5 p-3 rounded-xl flex flex-col gap-1">
          <p className="text-[8px] font-bold opacity-30 uppercase">Area</p>
          <p className="text-xs font-black">{area} sqft</p>
        </div>
        <div className="bg-white/5 p-3 rounded-xl flex flex-col gap-1">
          <p className="text-[8px] font-bold opacity-30 uppercase">BHK</p>
          <p className="text-xs font-black">{bhk}</p>
        </div>
      </div>

      <div className="h-[1px] bg-white/5 w-full" />

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4 text-[10px] font-bold opacity-40 uppercase">
           <div className="flex flex-col">
              <span className="text-[8px] opacity-50">₹/SQFT</span>
              <span>{psqft.toLocaleString()}</span>
           </div>
           <div className="flex flex-col border-l border-white/10 pl-4">
              <span className="text-[8px] opacity-50">{intent === 'Buy' ? 'YIELD' : 'FURNISH'}</span>
              <span>{intent === 'Buy' ? `${yld}%` : (item.furnishing_status || '–')}</span>
           </div>
        </div>
        <div className="px-2 py-1 rounded-md text-[10px] font-black bg-white/10">
          {score}/10
        </div>
      </div>
    </div>
  );
};
