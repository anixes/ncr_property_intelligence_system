import { IntelligenceSuite } from '@/types';
import { formatCurrency } from '@/lib/formatters';
import ScoreBadge from '../shared/ScoreBadge';

interface KpiResultProps {
  predictedRent: number;
  marketValue: number;
  intelligence: IntelligenceSuite;
  isBuy: boolean;
  area: number;
}

export default function KpiResult({ predictedRent, marketValue, intelligence, isBuy, area }: KpiResultProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 mt-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      
      {/* Box 1: Primary Value */}
      <div className="glass-card p-6 flex flex-col justify-center relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-32 h-32 bg-accent-primary opacity-10 blur-[80px] rounded-full group-hover:opacity-20 transition-opacity" />
        <span className="text-sm font-semibold text-foreground/50 tracking-wide uppercase mb-2">
          {isBuy ? 'Estimated Valuation' : 'Predicted Monthly Rent'}
        </span>
        <span className="text-4xl font-extrabold text-white tracking-tight">
          {formatCurrency(isBuy ? marketValue : predictedRent, isBuy ? 'buy' : 'rent')}
        </span>
        <span className="text-xs text-foreground/40 mt-1 font-mono">
          Fair Value Estimate based on ~43k records
        </span>
      </div>

      {/* Box 2: Secondary Metric */}
      <div className="glass-card p-6 flex flex-col justify-center border-accent-secondary/10 hover:border-accent-secondary/30 transition-colors">
        <span className="text-sm font-semibold text-foreground/50 tracking-wide uppercase mb-2">
          {isBuy ? 'Predicted Rent' : 'Fair Value (₹/sqft)'}
        </span>
        <span className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-foreground/50 font-mono">
          {isBuy ? formatCurrency(predictedRent, 'rent') : `₹ ${Math.round(marketValue / area).toLocaleString('en-IN')}`}
        </span>
        <span className="text-xs text-foreground/40 mt-2 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-accent-secondary animate-pulse" />
          Model Confidence: High
        </span>
      </div>

      {/* Box 3: Unified Score */}
      <div className="glass-card p-6 flex flex-col items-center justify-center text-center bg-gradient-to-br from-white/5 to-white/0">
        <span className="text-sm font-semibold text-foreground/50 tracking-wide uppercase mb-3">
          {isBuy ? 'Investment Score' : 'Deal Score'}
        </span>
        <ScoreBadge score={intelligence.unified_score} size="lg" />
        <span className="text-xs text-foreground/40 mt-3 max-w-[80%] mx-auto">
          Weighted combination of yield, locality trends, and amenities.
        </span>
      </div>

    </div>
  );
}
