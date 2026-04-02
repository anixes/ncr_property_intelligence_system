import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Target, Zap, Ruler, MapPin, Home, ArrowRight, BarChart3, ShieldCheck } from 'lucide-react';
import * as api from '@/lib/api';
import { PropertyInput } from '@/types';

export default function ValuationHUD({ initialCity }: { initialCity: string }) {
  const [city, setCity] = useState(initialCity === 'Entire NCR' ? 'Gurgaon' : initialCity);
  const [sector, setSector] = useState('');
  const [area, setArea] = useState(1200);
  const [propType, setPropType] = useState<'Apartment' | 'Independent House' | 'Villa'>('Apartment');
  const [localities, setLocalities] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [prediction, setPrediction] = useState<any>(null);

  useEffect(() => {
    const fetchLocs = async () => {
      const locs = await api.getLocalities(city);
      setLocalities(locs);
      if (locs.length > 0) setSector(locs[0]);
    };
    fetchLocs();
  }, [city]);

  const handleQuickPredict = async () => {
    setIsLoading(true);
    setPrediction(null);
    
    // Minimal valid input for prediction
    const input: PropertyInput = {
      listing_type: 'buy',
      city,
      sector,
      prop_type: propType,
      area,
      bedrooms: 3,
      bathrooms: 2,
      furnishing_status: 'Semi-Furnished',
      legal_status: 'Freehold',
      amenities: { has_pool: false, has_gym: false, has_lift: true, has_power_backup: true, is_gated_community: true },
      location_score: { is_near_metro: true, is_corner_property: false, is_park_facing: false, is_vastu_compliant: false },
      features: { is_luxury: false, is_servant_room: false, is_study_room: false, is_store_room: false, is_pooja_room: false }
    };

    try {
      const result = await api.predict(input);
      setPrediction(result);
    } catch (error) {
      console.error('Prediction failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">
      {/* Input Side: Quick Scan Portal */}
      <div className="bg-[#1c1b1b] border border-white/5 rounded-2xl p-8 flex flex-col justify-between shadow-2xl relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/5 blur-[100px] group-hover:bg-purple-500/10 transition-all" />
        
        <div className="relative z-10 space-y-8">
          <div className="space-y-1">
            <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
              <Zap className="w-5 h-5 text-purple-400" />
              Quick Scan Portal
            </h2>
            <p className="text-sm text-zinc-400 font-mono">Input core asset vectors for instant spatial valuation.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest flex items-center gap-2">
                <MapPin className="w-3 h-3" /> Jurisdiction
              </label>
              <select 
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full bg-[#050505] border-none rounded-xl py-3 px-4 text-sm text-white focus:ring-1 focus:ring-purple-500/50 outline-none transition-all cursor-pointer font-black uppercase"
              >
                {['Gurgaon', 'Noida', 'Greater Noida'].map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest flex items-center gap-2">
                <Target className="w-3 h-3" /> Locality
              </label>
              <select 
                value={sector}
                onChange={(e) => setSector(e.target.value)}
                className="w-full bg-[#050505] border-none rounded-xl py-3 px-4 text-sm text-white focus:ring-1 focus:ring-purple-500/50 outline-none transition-all cursor-pointer font-black uppercase"
              >
                {localities.map(l => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest flex items-center gap-2">
                <Home className="w-3 h-3" /> Asset Class
              </label>
              <select 
                value={propType}
                onChange={(e) => setPropType(e.target.value as any)}
                className="w-full bg-[#050505] border-none rounded-xl py-3 px-4 text-sm text-white focus:ring-1 focus:ring-purple-500/50 outline-none transition-all cursor-pointer font-black uppercase"
              >
                {['Apartment', 'Independent House', 'Villa'].map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest flex items-center gap-2">
                <Ruler className="w-3 h-3" /> Area (Sqft)
              </label>
              <input 
                type="number"
                value={area}
                onChange={(e) => setArea(Number(e.target.value))}
                className="w-full bg-[#050505] border-none rounded-xl py-3 px-4 text-sm text-white focus:ring-1 focus:ring-purple-500/50 outline-none transition-all font-mono font-black"
              />
            </div>
          </div>
        </div>

        <button 
          onClick={handleQuickPredict}
          disabled={isLoading}
          className="mt-12 w-full py-4 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-black font-black uppercase tracking-[0.2em] rounded-xl shadow-xl shadow-purple-900/20 transition-all flex items-center justify-center gap-3 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }} className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full" />
          ) : (
             <>Initiate Asset Valuation <ArrowRight className="w-4 h-4" /></>
          )}
        </button>
      </div>

      {/* Output Side: Analytical Feedback */}
      <div className="bg-[#050505] border border-white/5 rounded-2xl p-10 flex flex-col items-center justify-center text-center relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--brand-purple-glow)_0%,_transparent_70%)] opacity-5" />
        
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div 
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              <div className="w-32 h-32 border-2 border-purple-500/10 border-t-purple-500 rounded-full animate-spin flex items-center justify-center">
                <Target className="w-10 h-10 text-purple-400 animate-pulse" />
              </div>
              <div className="space-y-2">
                <p className="text-[10px] font-mono text-purple-400 uppercase tracking-[0.5em] animate-pulse">Analyzing Price Tensors...</p>
                <p className="text-zinc-600 text-[9px] uppercase tracking-widest font-mono">Mapping {sector} historic listing trends</p>
              </div>
            </motion.div>
          ) : prediction ? (
            <motion.div 
              key="prediction"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="w-full space-y-8"
            >
              <div className="space-y-2">
                <p className="text-[10px] font-mono text-zinc-500 uppercase tracking-[0.3em]">Estimated Market Value</p>
                <h3 className="text-5xl font-black text-white tracking-tighter">
                  ₹{Number(prediction.estimated_price).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                </h3>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-zinc-900/50 rounded-xl border border-white/5 space-y-1">
                  <p className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest">Confidence Score</p>
                  <p className="text-lg font-bold text-emerald-400 font-mono">{(prediction.confidence * 100).toFixed(1)}%</p>
                </div>
                <div className="p-4 bg-zinc-900/50 rounded-xl border border-white/5 space-y-1">
                  <p className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest">Price Range</p>
                  <p className="text-sm font-bold text-zinc-300 font-mono">₹{(prediction.estimated_price * 0.95 / 1000000).toFixed(1)}M - ₹{(prediction.estimated_price * 1.05 / 1000000).toFixed(1)}M</p>
                </div>
              </div>

              <div className="bg-purple-500/5 p-4 rounded-xl border border-purple-500/10 flex items-center gap-3 text-left">
                <ShieldCheck className="w-5 h-5 text-purple-400 shrink-0" />
                <p className="text-[10px] text-zinc-400 leading-relaxed italic">
                  Institutional Prediction Engine utilizes CatBoost regressors trained on 2M+ data points across {city}.
                </p>
              </div>
            </motion.div>
          ) : (
            <motion.div 
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <div className="w-32 h-32 border-2 border-white/5 rounded-full flex items-center justify-center opacity-20">
                <BarChart3 className="w-10 h-10 text-white" />
              </div>
              <p className="text-xs text-zinc-500 font-mono max-w-[200px] uppercase tracking-widest">Awaiting spatial coordinate input for {city} target</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
