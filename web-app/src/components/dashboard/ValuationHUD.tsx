'use client';

import React from 'react';
import { ValuationResponse } from '@/types';
import { TrendingUp, AlertTriangle, IndianRupee, ChartBar } from 'lucide-react';

interface Props {
  data: ValuationResponse;
}

export const ValuationHUD = ({ data }: Props) => {
  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(val);
  };

  const alphaScore = data.intelligence.alpha_score;
  const isValuePick = data.intelligence.risk_label === "VALUE PICK";

  return (
    <div className="space-y-8 lg:space-y-12 animate-in fade-in slide-in-from-bottom-5 duration-700">
      
      {/* HERO VALUATION OVERLAY */}
      <div className="bg-[#131314] rounded-[32px] sm:rounded-[48px] p-8 sm:p-12 lg:p-16 relative overflow-hidden group shadow-2xl border border-white/5">
        
        {/* Institutional Glow Overlay */}
        <div className="absolute top-0 right-0 w-64 sm:w-96 h-64 sm:h-96 bg-primary/10 blur-[120px] rounded-full -translate-y-1/2 translate-x-1/2 group-hover:bg-primary/20 transition-colors duration-1000" />
        
        <div className="relative z-10 space-y-12">
          
          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-10 sm:gap-12">
             <div className="space-y-4">
                <p className="text-[10px] sm:text-xs font-black uppercase tracking-[0.3em] text-[#adaaab] font-inter">Estimated Institutional Value</p>
                <h2 className="text-4xl sm:text-5xl lg:text-7xl font-black tracking-tightest leading-none font-headline text-white">
                  {formatCurrency(data.valuation.predicted_price)}
                </h2>
             </div>
             
             {/* Alpha HUD Cluster */}
             <div className="flex items-center gap-4 bg-black/40 p-4 sm:p-6 rounded-2xl sm:rounded-3xl backdrop-blur-3xl border border-white/5 shadow-inner self-start lg:self-auto">
                <div className="text-right">
                   <p className="text-[10px] font-black uppercase tracking-widest text-[#adaaab]">Alpha Score</p>
                   <p className="text-xl sm:text-2xl font-black font-headline text-primary">{alphaScore.toFixed(1)} <span className="text-xs text-white/50">/ 10</span></p>
                </div>
                <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-xl sm:rounded-2xl flex items-center justify-center bg-primary/10 text-primary">
                   <ChartBar className="w-6 h-6 sm:w-8 sm:h-8" />
                </div>
             </div>
          </div>
          
          {/* Metrics Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-10 pt-10 sm:pt-12 border-t border-white/5 items-stretch">
             <Metric label="Gross Yield" value={`${data.intelligence.financials.gross_yield.toFixed(1)}%`} icon={TrendingUp} color="text-green-400" bgColor="bg-green-400/10" />
             <Metric label="Risk Matrix" value={data.intelligence.risk_label} icon={AlertTriangle} color={isValuePick ? "text-green-400" : "text-amber-400"} bgColor={isValuePick ? "bg-green-400/10" : "bg-amber-400/10"} />
             <Metric label="Monthly Alpha" value={formatCurrency(data.intelligence.financials.estimated_monthly_rent)} icon={IndianRupee} color="text-primary" bgColor="bg-primary/10" />
             <Metric label="Confidence" value="94.2%" icon={ChartBar} color="text-blue-400" bgColor="bg-blue-400/10" />
          </div>

        </div>
      </div>
    </div>
  );
};

const Metric = ({ label, value, icon: Icon, color, bgColor }: any) => (
   <div className={`p-6 rounded-3xl border border-white/5 bg-white/[0.02] flex flex-col justify-between space-y-4 hover:bg-white/[0.04] transition-all`}>
      <div className="flex items-center gap-3">
         <div className={`p-2 rounded-lg ${bgColor}`}>
            <Icon className={`w-3.5 h-3.5 ${color}`} />
         </div>
         <span className="text-[10px] font-black uppercase tracking-widest text-[#adaaab] font-headline">{label}</span>
      </div>
      <p className={`text-xl sm:text-2xl font-black font-headline ${color}`}>{value}</p>
   </div>
);
