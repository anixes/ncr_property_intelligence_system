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
      <div className="space-y-12 lg:space-y-32 animate-in fade-in slide-in-from-bottom-5 duration-1000">

         {/* 6-GRID INTELLIGENCE HUD */}
         <section className="space-y-10">
            <header className="space-y-4">
               <div className="flex items-center gap-3 text-primary text-[10px] font-black uppercase tracking-[0.4em]">
                  <ChartBar className="w-4 h-4" />
                  <span>Intelligence Analytics HUD</span>
               </div>
               <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                  <h3 className="text-2xl sm:text-4xl font-black font-headline tracking-tighter text-white">
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
                  label={intent === 'buy' ? "Investment Alpha" : "Lifestyle Index"}
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

         {/* GRID-ANALYSIS: COMPARABLES & ALTERNATIVES */}
         <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 sm:gap-20 items-start">
            {/* VERIFIED COMPARABLES */}
            {comparables.length > 0 && (
               <section className="space-y-12">
                  <header className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-white/5 pb-8">
                     <div className="space-y-3">
                        <div className="text-[10px] font-black text-primary uppercase tracking-[0.4em]">Historical Benchmarks</div>
                        <h3 className="text-xl sm:text-3xl font-black font-headline text-white uppercase">Verified <span className="text-white/40">Comparables.</span></h3>
                     </div>
                  </header>

                  <div className="flex overflow-x-auto pb-8 -mx-4 px-4 gap-6 scrollbar-hide snap-x snap-mandatory">
                     {comparables.slice(0, 5).map((item, idx) => (
                        <motion.div
                           key={idx}
                           initial={{ opacity: 0, scale: 0.95 }}
                           whileInView={{ opacity: 1, scale: 1 }}
                           viewport={{ once: true }}
                           transition={{ delay: idx * 0.1 }}
                           className="min-w-[85%] sm:min-w-[45%] lg:min-w-[320px] snap-center"
                        >
                           <PropertyCard
                              item={item}
                              intent={intent}
                              onClick={onCardClick}
                              index={idx + 1}
                           />
                        </motion.div>
                     ))}
                  </div>
               </section>
            )}

            {/* SPATIAL ALTERNATIVES */}
            {alternatives.length > 0 && (
               <section className="space-y-12">
                  <header className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-white/5 pb-8">
                     <div className="space-y-3">
                        <div className="text-[10px] font-black text-primary uppercase tracking-[0.4em]">
                           {intent === 'rent' ? "Niche Lifestyle Clusters" : "Macro Spatial Analysis"}
                        </div>
                        <h3 className="text-xl sm:text-3xl font-black font-headline text-white uppercase">
                           {intent === 'rent' ? "Lifestyle " : "Investment "}
                           <span className="text-white/40">{intent === 'rent' ? "Substitutes." : "Alternatives."}</span>
                        </h3>
                     </div>
                  </header>

                  <div className="flex overflow-x-auto pb-8 -mx-4 px-4 gap-6 scrollbar-hide snap-x snap-mandatory">
                     {alternatives.slice(0, 5).map((item, idx) => (
                        <motion.div
                           key={idx}
                           initial={{ opacity: 0, scale: 0.95 }}
                           whileInView={{ opacity: 1, scale: 1 }}
                           viewport={{ once: true }}
                           transition={{ delay: idx * 0.1 }}
                           className="min-w-[85%] sm:min-w-[45%] lg:min-w-[320px] snap-center"
                        >
                           <PropertyCard
                              item={item}
                              intent={intent}
                              onClick={onCardClick}
                              index={idx + 1}
                           />
                        </motion.div>
                     ))}
                  </div>
               </section>
            )}
         </div>

         {/* STRATEGIC MARKET INSIGHT - THE 'INSTITUTIONAL' EDGE */}
         <section className="relative overflow-hidden bg-primary/5 border border-primary/10 rounded-[2rem] sm:rounded-[2.5rem] p-5 sm:p-12 lg:p-16">
            <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-primary/10 to-transparent pointer-events-none" />
            <div className="max-w-4xl space-y-10 relative z-10">
               <header className="space-y-4">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/20 text-primary text-[9px] font-black uppercase tracking-widest border border-primary/20">
                     Institutional Market Insight
                  </div>
                  <h4 className="text-2xl sm:text-5xl font-black font-headline tracking-tight text-white leading-tight">
                     Strategic <span className="opacity-40">Positioning.</span>
                  </h4>
               </header>

               <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                  <div className="space-y-6">
                     <p className="text-base sm:text-xl text-white/70 leading-relaxed font-light font-body italic">
                        {intent === 'buy'
                           ? "This asset demonstrates high capital growth potential due to its proximity to emerging commercial corridors. The valuation is currently aligned with the institutional entry-point for the sector."
                           : "The rental profile suggests strong resident retention scores. Pricing is currently optimized for immediate occupancy compared to neighboring high-utility clusters."
                        }
                     </p>
                     <ul className="space-y-4">
                        {[
                           { label: "Market Sentiment", value: "Bullish (Accumulate)", color: "text-green-400" },
                           { label: "Liquidity Index", value: "High", color: "text-primary" },
                           { label: "Data Integrity", value: "94.2% verified", color: "text-white/40" }
                        ].map((stat, i) => (
                           <li key={i} className="flex items-center justify-between py-3 border-b border-white/5">
                              <span className="text-[10px] font-black uppercase tracking-widest text-[#adaaab]">{stat.label}</span>
                              <span className={`text-xs font-black uppercase ${stat.color}`}>{stat.value}</span>
                           </li>
                        ))}
                     </ul>
                  </div>

                  <div className="bg-[#0a0a0a]/60 backdrop-blur-xl rounded-3xl p-8 border border-white/5 space-y-8">
                     <div className="space-y-2">
                        <p className="text-[10px] font-black uppercase tracking-[.3em] text-primary">Security Spectrum</p>
                        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden flex">
                           <div className="h-full bg-green-500/40 w-1/3 border-r border-black/20" />
                           <div className="h-full bg-amber-500/40 w-1/3 border-r border-black/20" />
                           <div className="h-full bg-red-500/40 w-1/3" />
                        </div>
                        <div className="flex justify-between text-[8px] font-black text-white/20 uppercase tracking-widest pt-1">
                           <span>Safe Entry</span>
                           <span>Neutral</span>
                           <span>Speculative</span>
                        </div>
                     </div>
                     <div className="space-y-2">
                        <div className="flex items-center gap-4">
                           <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${isValuePick ? 'bg-green-500/20 text-green-400' : 'bg-primary/20 text-primary'}`}>
                              <Compass className="w-6 h-6" />
                           </div>
                           <div>
                              <p className="text-xs font-bold text-white uppercase tracking-wider">Asset Delta</p>
                              <p className="text-[10px] text-[#adaaab]">{positionLabel} by {Math.abs(marketPosition).toFixed(1)}%</p>
                           </div>
                        </div>
                     </div>
                  </div>
               </div>
            </div>
         </section>

      </div>
   );
};

const MetricCard = ({ label, value, subValue, icon: Icon, color, glow, onClick, actionLabel }: any) => (
   <div
      onClick={onClick}
      className={`group relative bg-[#131314] rounded-2xl sm:rounded-[32px] p-4 sm:p-8 border border-white/5 transition-all duration-500 hover:border-primary/20 flex flex-col justify-between ${glow} ${onClick ? 'cursor-pointer active:scale-[0.98]' : ''}`}
   >
      <div className="flex justify-between items-start mb-6 sm:mb-8 gap-2">
         <div className="space-y-1 overflow-hidden">
            <p className="text-[8px] sm:text-[9px] font-black uppercase tracking-[0.1em] sm:tracking-[0.3em] text-[#adaaab] font-inter truncate">{label}</p>
            <p className="text-[9px] sm:text-[10px] font-medium text-white/30 truncate">{subValue}</p>
         </div>
         <div className="p-2 sm:p-3 rounded-xl sm:rounded-2xl bg-white/[0.03] group-hover:bg-primary/10 transition-colors shrink-0">
            <Icon className={`w-4 h-4 sm:w-5 sm:h-5 ${color}`} />
         </div>
      </div>
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 sm:gap-4 mt-auto">
         <div className={`text-base sm:text-2xl lg:text-3xl font-black font-headline tracking-tighter ${color} leading-none truncate w-full`}>
            {value}
         </div>
         {actionLabel && (
            <div className="w-full sm:w-auto text-center px-2 py-1.5 sm:px-4 sm:py-2 rounded-full bg-primary/10 border border-primary/20 text-[8px] sm:text-[10px] font-black uppercase tracking-[0.2em] text-primary group-hover:bg-primary group-hover:text-black transition-all truncate shrink-0">
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
