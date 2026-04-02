'use client';

import { Suspense } from 'react';
import PropertyForm from '@/components/analyzer/PropertyForm';
import ValuationBlock from '@/components/analyzer/ValuationBlock';
import RoiBreakdown from '@/components/analyzer/RoiBreakdown';
import PropertyCard from '@/components/shared/PropertyCard';
import AlternativeCard from '@/components/shared/AlternativeCard';
import ScoreBadge from '@/components/shared/ScoreBadge';
import { usePredict } from '@/hooks/usePredict';
import { AlertTriangle, Layers, TrendingUp } from 'lucide-react';
import { PropertyInput, Recommendation } from '@/types';
import { formatCurrency, formatYield } from '@/lib/formatters';

export default function AnalyzerPage() {
  const { data, isLoading, error, mutate } = usePredict();

  const handleRunAnalytics = (input: PropertyInput) => {
    mutate(input);
  };

  return (
    <div className="flex-1 max-w-[1400px] mx-auto w-full px-6 lg:px-12 py-16">
      
      <div className="mb-12">
        <h1 className="text-4xl font-black tracking-tighter text-slate-900 flex items-center gap-4">
          Market Analyzer
          <span className="text-[10px] bg-blue-50 text-blue-800 px-2.5 py-1 rounded-md uppercase tracking-[0.2em] font-black border border-blue-100 shadow-sm">
            V2.0 Institutional
          </span>
        </h1>
        <p className="text-slate-500 mt-3 max-w-2xl text-lg font-medium leading-relaxed">
          Run deep valuation scans against 43,000+ localized market records. 
          Identify trends, analyze yield impact, and optimize your portfolio in real-time.
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-16">
        
        {/* Left Sidebar: Interactive Inputs */}
        <div className="w-full lg:w-[420px] flex-shrink-0">
          <div className="sticky top-28 bg-white border border-slate-100 rounded-3xl p-2 shadow-xl shadow-slate-200/20">
            <PropertyForm onSubmit={handleRunAnalytics} isLoading={isLoading} />
          </div>
        </div>

        {/* Right Content Area: Results Display */}
        <div className="flex-1 min-w-0 flex flex-col gap-12">
          
          {error && (
            <div className="p-6 bg-red-50 border border-red-100 rounded-2xl flex items-start gap-4 text-red-600">
               <AlertTriangle className="w-6 h-6 flex-shrink-0 mt-0.5" />
               <div>
                 <p className="font-black uppercase tracking-widest text-[11px]">Intelligence Engine Error</p>
                 <p className="text-red-600/80 mt-1 font-bold">{error}</p>
               </div>
            </div>
          )}

          {!data && !isLoading && !error && (
            <div className="flex flex-col items-center justify-center p-16 text-center rounded-[32px] border-2 border-dashed border-slate-200 bg-slate-50/50 h-[500px]">
              <div className="p-6 bg-white shadow-xl shadow-slate-200/40 rounded-3xl mb-8">
                <Layers className="w-10 h-10 text-blue-800" />
              </div>
              <h3 className="text-2xl font-black text-slate-900 uppercase tracking-tighter">Awaiting Parameters</h3>
              <p className="text-slate-500 max-w-md mt-4 font-medium leading-relaxed">
                Configure your property details in the left panel. Our models will cross-reference 43,000+ data points to generate an instant institutional-grade appraisal.
              </p>
            </div>
          )}

          {data && (
            <div className="animate-in fade-in slide-in-from-bottom-12 duration-1000 space-y-16">
              
              {/* PRIMARY DECISION BLOCK */}
              <ValuationBlock 
                marketValue={data.estimated_market_value}
                intelligence={data.intelligence_suite}
              />

              {/* SECONDARY INSIGHTS GRID */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="bg-white rounded-3xl border border-slate-50 p-8 shadow-sm flex flex-col gap-2">
                   <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Predicted Market Rent</div>
                   <div className="text-2xl font-black text-slate-900">{formatCurrency(data.predicted_monthly_rent, 'rent')}</div>
                   <div className="text-xs text-slate-400 font-bold mt-1">~ ₹{(data.predicted_monthly_rent / (data.similar_listings[0]?.area || 1000)).toFixed(1)}/sqft yield rate</div>
                </div>

                <div className="bg-white rounded-3xl border border-slate-50 p-8 shadow-sm flex flex-col gap-2">
                   <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Gross Investment Yield</div>
                   <div className="text-2xl font-black text-blue-700">
                     {formatYield(data.intelligence_suite.yield_pct).label}
                     {formatYield(data.intelligence_suite.yield_pct).flag === 'anomaly' && (
                       <span className="ml-2 text-xs bg-amber-50 text-amber-700 px-2 py-0.5 rounded font-black uppercase tracking-tighter">Anomaly</span>
                     )}
                   </div>
                   <div className="text-xs text-slate-400 font-bold mt-1">Comparison to area median yield</div>
                </div>

                <div className="bg-white rounded-3xl border border-slate-50 p-8 shadow-sm flex flex-col items-center justify-center text-center">
                   <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3">Institutional Rating</div>
                   <ScoreBadge score={data.intelligence_suite.unified_score} size="lg" />
                </div>
              </div>

              <div className="bg-white rounded-[32px] border border-slate-100 p-10 shadow-sm">
                <h3 className="text-[11px] font-black text-slate-400 uppercase tracking-[0.25em] flex items-center gap-2.5 mb-10">
                  <TrendingUp className="w-4 h-4 text-blue-800" /> ROI & Market Outlook Profile
                </h3>
                <RoiBreakdown 
                  intelligence={data.intelligence_suite} 
                  metroDist={data.dist_to_metro_km} 
                />
              </div>

              {/* Verified Comparables Matrix */}
              {data.similar_listings && data.similar_listings.length > 0 && (
                <div className="space-y-10">
                  <div className="flex justify-between items-end">
                    <h2 className="text-2xl font-black text-slate-900 uppercase tracking-tighter flex items-center gap-3">
                      Comparable Sales (Basis for Valuation)
                    </h2>
                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] hidden sm:inline-block border-b border-slate-200 pb-1">
                      Sorted by Valuation Match
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
                    {data.similar_listings.map((prop, idx) => (
                      <PropertyCard 
                        key={`comp-${idx}`} 
                        property={prop} 
                        subjectPrice={data.estimated_market_value}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Strategic Market Allocations */}
              {data.recommendations && data.recommendations.length > 0 && (
                <div className="pt-8 border-t border-slate-100">
                   <h2 className="text-2xl font-black text-slate-900 uppercase tracking-tighter mb-4">
                      Strategic Market Allocations
                   </h2>
                   <p className="text-lg text-slate-500 mb-10 max-w-4xl font-medium leading-relaxed">
                     Based on ML models scanning the broader NCR region, these alternative sectors offer optimized yield profiles compared to the selected area.
                   </p>
                   
                   <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
                     {data.recommendations.map((rec: Recommendation, idx: number) => (
                        <AlternativeCard 
                          key={`alt-${idx}`}
                          locality={rec.locality}
                          city={rec.city}
                          distanceKm={rec.distance_km}
                          yieldPct={rec.expected_yield_pct}
                          compositeScore={rec.composite_score}
                          pricePerSqft={rec.median_price_sqft}
                          isBuy={true}
                          rank={idx + 1}
                        />
                     ))}
                   </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
