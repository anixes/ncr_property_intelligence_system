'use client';

import React from 'react';
import { PredictionResponse, PropertyAsset, Recommendation } from '@/types';
import { IndianRupee, ChartBar, Compass, Sparkles, TrendingUp, AlertTriangle } from 'lucide-react';
import { formatNCRPrice } from '@/utils/format';
import { PropertyCard } from './PropertyCard';
import { motion } from 'framer-motion';

interface Props {
  data: PredictionResponse;
  intent: 'buy' | 'rent';
  onCardClick?: (item: PropertyAsset | Recommendation) => void;
}

export const ValuationHUD = ({ data, intent, onCardClick }: Props) => {
  const alphaScore = data?.intelligence_suite?.unified_score || 0;
  const isValuePick = data?.intelligence_suite?.risk_analysis?.label === "VALUE PICK";
  const marketPosition = data?.intelligence_suite?.overvaluation_pct || 0;
  const positionLabel = marketPosition < 0 ? "UNDERVALUED" : "OVERVALUED";
  const positionColor = marketPosition < 0 ? "text-green-400" : "text-amber-400";
  
  const comparables = data?.similar_listings || [];
  const alternatives = data?.recommendations || [];

  return (
    <div className="space-y-20 lg:space-y-32 animate-in fade-in slide-in-from-bottom-5 duration-1000">
      
      {/* 6-GRID INTELLIGENCE HUD */}
      <section className="space-y-10">
        <header className="space-y-4">
           <div className="flex items-center gap-3 text-primary text-[10px] font-black uppercase tracking-[0.4em]">
              <ChartBar className="w-4 h-4" />
              <span>Intelligence Analytics HUD</span>
           </div>
           <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
             <h3 className="text-3xl sm:text-4xl font-black font-headline tracking-tighter text-white">
                Market <span className="text-white/40">Performance.</span>
             </h3>
             <p className="text-[10px] font-bold text-white/20 uppercase tracking-[0.2em] animate-pulse">
                Click any asset below for Strategic Deep Dive
             </p>
           </div>
        </header>

        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-8">
           {intent === 'buy' ? (
             <>
               <MetricCard 
                  label="Standard Valuation" 
                  value={formatNCRPrice(data.estimated_market_value)} 
                  subValue="Institutional Benchmark"
                  icon={IndianRupee} 
                  color="text-white" 
                  glow="group-hover:shadow-[0_0_30px_rgba(255,255,255,0.05)] cursor-pointer"
                  onClick={() => data.asset && onCardClick?.(data.asset)}
                  actionLabel="View Analysis"
               />
               <MetricCard 
                  label="Rental Potential" 
                  value={formatNCRPrice(data.predicted_monthly_rent)} 
                  subValue="Target Asset Alpha"
                  icon={TrendingUp} 
                  color="text-primary" 
                  glow="group-hover:shadow-[0_0_30px_rgba(189,157,255,0.15)]"
               />
             </>
           ) : (
             <>
               <MetricCard 
                  label="Monthly Rent" 
                  value={formatNCRPrice(data.predicted_monthly_rent)} 
                  subValue="Resident Monthly Overhead"
                  icon={TrendingUp} 
                  color="text-primary" 
                  glow="group-hover:shadow-[0_0_30px_rgba(189,157,255,0.15)] cursor-pointer"
                  onClick={() => data.asset && onCardClick?.(data.asset)}
                  actionLabel="View Analysis"
               />
               <MetricCard 
                  label="Capital Benchmark" 
                  value={formatNCRPrice(data.estimated_market_value)} 
                  subValue="Buy-Back Value"
                  icon={IndianRupee} 
                  color="text-white/60" 
                  glow="group-hover:shadow-[0_0_30px_rgba(255,255,255,0.05)]"
               />
             </>
           )}
           <MetricCard 
              label={intent === 'buy' ? "Investment Score" : "Lifestyle Index"} 
              value={`${(alphaScore).toFixed(1)} / 10`} 
              subValue={intent === 'buy' ? "Unified Asset Delta" : "Utility Performance"}
              icon={intent === 'buy' ? ChartBar : Sparkles} 
              color="text-primary" 
              glow="group-hover:shadow-[0_0_30px_rgba(189,157,255,0.15)]"
           />
           {intent === 'buy' ? (
             <MetricCard 
                label="Gross Rental Yield" 
                value={`${(data?.intelligence_suite?.yield_pct || 0).toFixed(2)}%`} 
                subValue="Annualized Performance"
                icon={TrendingUp} 
                color="text-green-400" 
                glow="group-hover:shadow-[0_0_30px_rgba(74,222,128,0.1)]"
             />
           ) : (
             <MetricCard 
                label="Security Deposit" 
                value={formatNCRPrice(data.predicted_monthly_rent * 2)} 
                subValue="NCR Standard (2 Months)"
                icon={IndianRupee} 
                color="text-primary" 
                glow="group-hover:shadow-[0_0_30px_rgba(189,157,255,0.15)]"
             />
           )}
           <MetricCard 
              label="Risk Stratification" 
              value={data?.intelligence_suite?.risk_analysis?.label || "NEUTRAL"} 
              subValue={`${data?.intelligence_suite?.risk_analysis?.confidence || 'High'} Confidence`}
              icon={AlertTriangle} 
              color={isValuePick ? "text-green-400" : "text-amber-400"} 
              glow={isValuePick ? "group-hover:shadow-[0_0_30_rgba(74,222,128,0.1)]" : "group-hover:shadow-[0_0_30_rgba(251,191,36,0.1)]"}
           />
           <MetricCard 
              label="Market position" 
              value={`${Math.abs(marketPosition).toFixed(1)}%`} 
              subValue={positionLabel}
              icon={Compass} 
              color={positionColor} 
              glow="group-hover:shadow-[0_0_30px_rgba(255,255,255,0.05)]"
           />
        </div>
      </section>

      {/* VERIFIED COMPARABLES */}
      {comparables.length > 0 && (
        <section className="space-y-12">
           <header className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-white/5 pb-8">
              <div className="space-y-3">
                 <div className="text-[10px] font-black text-primary uppercase tracking-[0.4em]">Historical Benchmarks</div>
                 <h3 className="text-3xl font-black font-headline text-white uppercase">Verified <span className="text-white/40">Comparables.</span></h3>
              </div>
              <p className="text-[10px] font-bold text-white/30 uppercase tracking-widest">Real-World Marketplace Matches</p>
           </header>

           <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {comparables.slice(0, 4).map((item, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <PropertyCard 
                    item={item} 
                    intent={intent} 
                    onClick={onCardClick}
                  />
                </motion.div>
              ))}
           </div>
        </section>
      )}

      {/* INVESTMENT ALTERNATIVES */}
      {alternatives.length > 0 && (
        <section className="space-y-12">
           <header className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-white/5 pb-8">
              <div className="space-y-3">
                 <div className="text-[10px] font-black text-primary uppercase tracking-[0.4em]">Macro Spatial Analysis</div>
                 <h3 className="text-3xl font-black font-headline text-white uppercase">Investment <span className="text-white/40">Alternatives.</span></h3>
              </div>
              <p className="text-[10px] font-bold text-white/30 uppercase tracking-widest">Neighboring Micro-Market Opportunities</p>
           </header>

           <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {alternatives.slice(0, 4).map((item, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <PropertyCard 
                    item={item} 
                    intent={intent} 
                    onClick={onCardClick}
                  />
                </motion.div>
              ))}
           </div>
        </section>
      )}

    </div>
  );
};

const MetricCard = ({ label, value, subValue, icon: Icon, color, glow, onClick, actionLabel }: any) => (
  <div 
    onClick={onClick}
    className={`group relative bg-[#131314] rounded-[32px] p-8 border border-white/5 transition-all duration-500 hover:border-primary/20 ${glow} ${onClick ? 'cursor-pointer active:scale-[0.98]' : ''}`}
  >
     <div className="flex justify-between items-start mb-8">
        <div className="space-y-1">
           <p className="text-[9px] font-black uppercase tracking-[0.3em] text-[#adaaab] font-inter">{label}</p>
           <p className="text-[10px] font-medium text-white/30">{subValue}</p>
        </div>
        <div className="p-3 rounded-2xl bg-white/[0.03] group-hover:bg-primary/10 transition-colors">
           <Icon className={`w-5 h-5 ${color}`} />
        </div>
     </div>
     <div className="flex items-end justify-between gap-4">
       <div className={`text-2xl sm:text-3xl font-black font-headline tracking-tighter ${color}`}>
          {value}
       </div>
       {actionLabel && (
         <div className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[8px] font-black uppercase tracking-widest text-primary group-hover:bg-primary group-hover:text-black transition-all">
           {actionLabel}
         </div>
       )}
     </div>
  </div>
);

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
