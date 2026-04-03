'use client';

import React, { useState } from 'react';
import { predictProperty } from '@/lib/api';
import { PredictionInput, ValuationResponse } from '@/types';
import { ValuationHUD } from '@/components/dashboard/ValuationHUD';
import { Loader2, MapPin, Building, Ruler, Send } from 'lucide-react';

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ValuationResponse | null>(null);
  const [input, setInput] = useState<PredictionInput>({
    city: 'Gurgaon',
    sector: 'Sector 54',
    property_name: 'The Camellias',
    bhk: 4,
    area: 9500,
    age: '0-1 Year',
    facing: 'North-East',
  });

  const handlePredict = async () => {
    setLoading(true);
    try {
      const data = await predictProperty(input);
      setResult(data);
    } catch (e) {
       console.error("Prediction failed", e);
    } finally { setLoading(false); }
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20 lg:py-24 space-y-24 md:space-y-32">
      
      {/* HEADER PORTER */}
      <header className="space-y-6 sm:space-y-8">
        <div className="inline-flex items-center gap-3 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-[10px] font-black uppercase tracking-[0.4em] border border-primary/10 font-body">
           Market Intelligence Porter
        </div>
        <div className="space-y-4">
          <h1 className="text-4xl sm:text-5xl lg:text-7xl font-black font-headline tracking-tightest leading-[0.9] text-white">
             Market <br className="hidden sm:block"/>
             <span className="text-[#adaaab]">Analyzer.</span>
          </h1>
          <p className="text-lg sm:text-xl md:text-2xl text-[#adaaab] font-light max-w-xl leading-relaxed tracking-tight font-body italic">
            High-fidelity property valuation targeting society-level price premiums in the NCR region.
          </p>
        </div>
      </header>

      {/* INPUT PORTER GRID */}
      <div className="bg-[#131314] rounded-[32px] sm:rounded-[48px] p-8 sm:p-12 md:p-16 relative overflow-hidden shadow-2xl border border-white/5">
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-10 items-start">
           <InputPorter label="Geography" value={input.city} onChange={(v) => setInput({...input, city: v})} icon={MapPin} />
           <InputPorter label="Micro Market" value={input.sector} onChange={(v) => setInput({...input, sector: v})} icon={MapPin} />
           <InputPorter label="Asset Name" value={input.property_name} onChange={(v) => setInput({...input, property_name: v})} icon={Building} />
           <InputPorter label="Blueprint BHK" value={input.bhk} onChange={(v) => setInput({...input, bhk: parseInt(v) || 0})} icon={Ruler} type="number" />
        </div>

        <div className="mt-12 sm:mt-16 pt-12 sm:pt-16 border-t border-white/5 flex flex-col lg:flex-row items-stretch lg:items-end justify-between gap-10 sm:gap-12">
           
           <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 sm:gap-10 flex-1">
              <div className="space-y-4">
                 <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.3em] text-primary">Area (SQFT)</div>
                 <input 
                    type="number" 
                    value={input.area} 
                    onChange={(e) => setInput({...input, area: parseInt(e.target.value) || 0})} 
                    className="bg-transparent text-2xl sm:text-3xl font-black font-headline outline-none text-white border-b border-white/10 focus:border-primary transition-all w-full min-h-[44px]" 
                 />
              </div>
              <div className="space-y-4">
                 <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.3em] text-primary">Age Matrix</div>
                 <div className="relative">
                    <select 
                        value={input.age} 
                        onChange={(e) => setInput({...input, age: e.target.value})} 
                        className="bg-transparent text-lg sm:text-xl font-black font-headline outline-none text-white border-b border-white/10 focus:border-primary transition-all w-full cursor-pointer appearance-none min-h-[44px]"
                    >
                        <option value="0-1 Year">0-1 Year</option>
                        <option value="1-5 Years">1-5 Years</option>
                        <option value="5-10 Years">5-10 Years</option>
                        <option value="10+ Years">10+ Years</option>
                    </select>
                 </div>
              </div>
           </div>

           <button 
             onClick={handlePredict}
             disabled={loading}
             className="w-full lg:w-max bg-primary text-black font-black text-[10px] uppercase tracking-widest rounded-xl sm:rounded-2xl h-14 sm:h-16 px-10 flex items-center justify-center gap-4 hover:brightness-110 active:scale-95 transition-all shadow-xl shadow-primary/20 disabled:opacity-50"
           >
             {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
             Analysis Result
           </button>
        </div>
      </div>

      {result && <ValuationHUD data={result} />}
    </div>
  );
}

const InputPorter = ({ label, value, onChange, icon: Icon, type = 'text' }: { label: string, value: any, onChange: (v: string) => void, icon: any, type?: string }) => (
  <div className="space-y-4 group">
    <div className="flex items-center gap-3">
       <Icon className="w-3.5 h-3.5 text-primary/30 group-focus-within:text-primary transition-colors" />
       <span className="text-[10px] font-black uppercase tracking-[0.4em] text-[#adaaab] font-body">{label}</span>
    </div>
    <input 
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full bg-white/[0.03] border border-white/5 rounded-xl sm:rounded-2xl p-4 sm:p-5 text-sm sm:text-base font-black font-headline text-white transition-all focus:bg-white/[0.07] focus:border-primary/30 outline-none min-h-[48px]"
    />
  </div>
);
