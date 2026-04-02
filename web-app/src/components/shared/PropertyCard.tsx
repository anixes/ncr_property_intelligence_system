import { PropertyListing } from '@/types';
import { formatCurrency, getMarketJudgment, formatYield } from '@/lib/formatters';
import { useShortlist } from '@/hooks/useShortlist';
import { MapPin, Maximize, TrendingUp, Bookmark } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface PropertyCardProps {
  property: PropertyListing;
  subjectPrice?: number;
}

export default function PropertyCard({ property, subjectPrice }: PropertyCardProps) {
  const { toggleShortlist, isInShortlist } = useShortlist();
  const isBuy = property.listing_type === 'buy';
  const isSaved = isInShortlist(property);
  
  const safeArea = Math.max(1, property.area);
  const delta = subjectPrice ? ((property.price - subjectPrice) / subjectPrice) : (property.unified_score > 7.5 ? -0.05 : 0);
  const judgment = getMarketJudgment(delta);
  const yieldInfo = formatYield(property.yield_pct / 100);

  const slug = property.society.replace(/\s+/g, '-').toLowerCase();
  const detailUrl = `/property/${slug}?s=${encodeURIComponent(property.society)}&l=${encodeURIComponent(property.locality)}&c=${encodeURIComponent(property.city)}&p=${property.price}&a=${safeArea}&b=${property.bhk}&y=${property.yield_pct/100}&v=${delta}`;

  return (
    <Link href={detailUrl} className="@container group block h-full">
      <div className="institutional-card p-6 md:p-8 flex flex-col gap-6 relative overflow-hidden h-full group-hover:border-primary/40 transition-all duration-500">
        
        {/* Shortlist Action */}
        <button 
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); toggleShortlist(property); }}
          className={cn(
            "absolute top-6 right-6 p-2.5 rounded-xl transition-all z-20",
            isSaved 
              ? "bg-primary text-white shadow-[0_0_20px_rgba(var(--brand-purple-glow),0.4)] scale-110" 
              : "bg-white/5 text-white/20 hover:text-primary hover:bg-white/10 border border-white/5"
          )}
        >
          <Bookmark className={cn("w-4 h-4", isSaved && "fill-current")} />
        </button>

        {/* Header: Identity & Judgment */}
        <div className="flex flex-col gap-2 pr-10">
          <div className="flex items-center gap-3">
            <h3 className="font-black text-xl text-white truncate uppercase tracking-tighter group-hover:text-primary transition-colors">
              {property.society}
            </h3>
            <div className={cn(
               "shrink-0 px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border",
               delta <= 0 ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "bg-white/5 text-white/40 border-white/10"
            )}>
              {judgment.icon} {judgment.label}
            </div>
          </div>
          <div className="flex items-center gap-1.5 text-[10px] font-black uppercase tracking-[0.2em] text-white/40">
            <MapPin className="w-3 h-3 text-primary" />
            <span className="truncate">{property.locality}</span>
          </div>
        </div>

        {/* Price & Delta Logic */}
        <div className="flex flex-col gap-1">
          <div className="text-4xl font-black text-white group-hover:text-primary transition-colors duration-500 tracking-tighter">
            {formatCurrency(property.price, isBuy ? 'buy' : 'rent')}
          </div>
          <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-white/20">
            <span className="text-white/60">₹{Math.round(property.price_per_sqft).toLocaleString('en-IN')}/sqft</span>
            <span className="w-1 h-1 rounded-full bg-white/10" />
            <span className={cn(delta <= 0 ? "text-emerald-400" : "text-amber-500")}>
              {delta < 0 ? '−' : '+'}{Math.abs(delta * 100).toFixed(0)}% vs Area
            </span>
          </div>
        </div>

        {/* Technical Data Grid */}
        <div className="grid grid-cols-2 gap-6 pt-6 border-t border-white/5 mt-auto">
          <div className="flex flex-col gap-1.5">
            <div className="text-[9px] font-black uppercase tracking-[0.2em] text-white/20 flex items-center gap-2">
              <Maximize className="w-3.5 h-3.5" /> Area
            </div>
            <div className="text-sm font-black text-white">
              {property.area} <span className="text-white/40">sqft</span>
              <span className="ml-2 px-2 py-0.5 bg-white/5 rounded-md text-[9px] text-primary">{property.bhk} BHK</span>
            </div>
          </div>

          <div className="flex flex-col gap-1.5 items-end text-right">
            <div className="text-[9px] font-black uppercase tracking-[0.2em] text-white/20 flex items-center justify-end gap-2">
              <TrendingUp className={cn("w-3.5 h-3.5", yieldInfo.flag === 'anomaly' ? "text-amber-500" : "text-emerald-500")} /> Yield
            </div>
            <div className={cn("text-sm font-black", yieldInfo.flag === 'anomaly' ? "text-amber-400" : "text-white")}>
              {yieldInfo.label}
            </div>
          </div>

          {/* Perf Bar: Institutional Confidence */}
          <div className="col-span-2 space-y-3 pt-2">
            <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
              <div 
                className={cn(
                  "h-full transition-all duration-1000 shadow-[0_0_10px_rgba(var(--brand-purple-glow),0.3)]",
                  yieldInfo.flag === 'anomaly' ? "bg-amber-400" : "bg-primary"
                )}
                style={{ width: `${Math.min(property.yield_pct, 10)}0%` }}
              />
            </div>
            <div className="flex justify-between items-center text-[8px] font-black text-white/10 uppercase tracking-[0.4em]">
              <span>Institutional Grade Match</span>
              <span className="text-white/20">Alpha Node 0.82</span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
