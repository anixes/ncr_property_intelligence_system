import { formatCurrency } from '@/lib/formatters';
import { MapPin, TrendingUp, Compass } from 'lucide-react';
import ScoreBadge from '../shared/ScoreBadge';

interface AlternativeCardProps {
  locality: string;
  city: string;
  pricePerSqft: number;
  yieldPct: number;
  distanceKm: number;
  compositeScore: number;
  isBuy: boolean;
  rank?: number;
  comparisonLocality?: string;
}

export default function AlternativeCard({
  locality,
  city,
  pricePerSqft,
  yieldPct,
  distanceKm,
  compositeScore,
  isBuy,
  rank,
  comparisonLocality
}: AlternativeCardProps) {
  return (
    <div className="bg-white border border-slate-100 p-6 rounded-3xl flex flex-col gap-6 shadow-sm hover:shadow-xl hover:border-blue-100 transition-all duration-300 group relative overflow-hidden">
      
      {rank && (
        <div className="absolute top-0 left-0 bg-blue-700 text-white px-3 py-1 text-[10px] font-black uppercase tracking-widest rounded-br-2xl shadow-sm z-10">
          Rank #{rank}
        </div>
      )}

      <div className="flex justify-between items-start pt-2">
        <div className="flex flex-col gap-1">
          <h4 className="font-black text-slate-900 text-base leading-tight">
            {locality} <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">{city}</span>
          </h4>
          <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1.5 mt-1">
            <Compass className="w-3.5 h-3.5 text-blue-800" />
            {distanceKm.toFixed(1)} km from search center
          </div>
        </div>
        <ScoreBadge score={compositeScore} size="sm" />
      </div>

      <div className="grid grid-cols-2 gap-4 mt-2 pt-5 border-t border-slate-50">
        <div className="flex flex-col gap-1">
          <span className="text-[10px] uppercase font-black text-slate-400 tracking-[0.1em]">
            {isBuy ? 'Avg Market Price' : 'Avg Rent'}
          </span>
          <span className="text-sm font-black text-blue-800">
            {isBuy ? `₹ ${pricePerSqft.toLocaleString('en-IN')}/sqft` : formatCurrency(pricePerSqft, 'rent')}
          </span>
        </div>
        
        <div className="flex flex-col items-end gap-1">
          <span className="text-[10px] uppercase font-black text-slate-400 tracking-[0.1em] flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5 text-emerald-600" /> Est. Yield
          </span>
          <span className="text-sm font-black text-slate-900">
            {(yieldPct * 100).toFixed(2)}%
          </span>
        </div>

        {rank === 1 && (
          <div className="col-span-2 mt-2 py-2 px-3 bg-emerald-50 border border-emerald-100 rounded-xl flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-emerald-700 animate-pulse">
            <span>Better yield than your target area</span>
            <span>+{(yieldPct * 100 - 3.2).toFixed(1)}% advantage</span>
          </div>
        )}
      </div>

    </div>
  );
}

