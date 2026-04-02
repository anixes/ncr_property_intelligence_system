import { IntelligenceSuite } from '@/types';
import { Target, TrendingUp, AlertTriangle, Train } from 'lucide-react';

interface RoiBreakdownProps {
  intelligence: IntelligenceSuite;
  metroDist?: number;
}

export default function RoiBreakdown({ intelligence, metroDist }: RoiBreakdownProps) {
  return (
    <div className="flex flex-wrap gap-4 mt-6">
      
      {/* Gross Yield Chip */}
      <div className="flex items-center gap-3 px-4 py-2.5 glass-card rounded-full whitespace-nowrap">
        <div className="p-1.5 bg-accent-primary/20 rounded-full text-accent-primary">
          <TrendingUp className="w-4 h-4" />
        </div>
        <div className="flex flex-col">
          <span className="text-[10px] uppercase font-bold text-foreground/50 tracking-wider">Gross Yield</span>
          <span className="font-mono font-bold text-sm text-accent-primary">
            {intelligence.yield_pct.toFixed(2)}%
          </span>
        </div>
      </div>

      {/* Risk Analysis Chip */}
      <div className="flex items-center gap-3 px-4 py-2.5 glass-card rounded-full whitespace-nowrap">
        <div className="p-1.5 bg-amber-500/20 rounded-full text-amber-500">
          <Target className="w-4 h-4" />
        </div>
        <div className="flex flex-col">
          <span className="text-[10px] uppercase font-bold text-foreground/50 tracking-wider">Market Position</span>
          <span className="font-semibold text-sm text-amber-500">
            {intelligence.risk_analysis.label}
          </span>
        </div>
      </div>

      {/* Overvaluation Metric */}
      <div className="flex items-center gap-3 px-4 py-2.5 glass-card rounded-full whitespace-nowrap">
        <div className="p-1.5 bg-red-500/20 rounded-full text-red-500">
          <AlertTriangle className="w-4 h-4" />
        </div>
        <div className="flex flex-col">
          <span className="text-[10px] uppercase font-bold text-foreground/50 tracking-wider">Overvaluation</span>
          <span className="font-mono font-bold text-sm text-red-500">
            {intelligence.overvaluation_pct.toFixed(1)}% vs area median
          </span>
        </div>
      </div>

      {/* Metro Proximity (Optional) */}
      {metroDist && (
        <div className="flex items-center gap-3 px-4 py-2.5 glass-card rounded-full whitespace-nowrap border-accent-secondary/30 bg-accent-secondary/5">
          <div className="p-1.5 bg-accent-secondary/20 rounded-full text-accent-secondary">
            <Train className="w-4 h-4" />
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] uppercase font-bold text-foreground/50 tracking-wider">Metro Connectivity</span>
            <span className="font-mono font-bold text-sm text-accent-secondary">
              ~{metroDist.toFixed(1)} km away
            </span>
          </div>
        </div>
      )}

    </div>
  );
}
