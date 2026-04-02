import { cn } from '@/lib/utils';
import { Trophy } from 'lucide-react';

interface ScoreBadgeProps {
  score: number;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function ScoreBadge({ score, label, size = 'md' }: ScoreBadgeProps) {
  const isHighAlpha = score >= 8.5;
  
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[9px]',
    md: 'px-3 py-1 text-[11px]',
    lg: 'px-4 py-2 text-xs',
  };

  return (
    <div className={cn(
      "flex items-center gap-2 font-black uppercase tracking-widest rounded-lg border",
      isHighAlpha 
        ? "bg-blue-50 border-blue-200 text-blue-700 shadow-sm shadow-blue-500/5" 
        : "bg-slate-50 border-slate-200 text-slate-500",
      sizeClasses[size]
    )}>
      <div className={cn(
        "w-1.5 h-1.5 rounded-full",
        isHighAlpha ? "bg-blue-600 animate-pulse" : "bg-slate-300"
      )} />
      <span>{isHighAlpha ? 'AA+' : 'Valuation'}: {score.toFixed(1)}</span>
      {label && <span className="text-slate-400 ml-1">{label}</span>}
    </div>
  );
}
