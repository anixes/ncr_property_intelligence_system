'use client';

import { useState, useEffect } from 'react';
import { PropertyInput } from '@/types';
import { CITIES, PROPERTY_TYPES, BHK_OPTIONS } from '@/lib/constants';
import { ChevronDown, ChevronUp, MapPin, Ruler, Home, Filter, BarChart3, ArrowRight } from 'lucide-react';
import api from '@/lib/api';
import { cn } from '@/lib/utils';

interface PropertyFormProps {
  onSubmit: (input: PropertyInput) => void;
  isLoading: boolean;
}

export default function PropertyForm({ onSubmit, isLoading }: PropertyFormProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [localities, setLocalities] = useState<string[]>([]);
  const [isFetchingLocalities, setIsFetchingLocalities] = useState(false);

  const [form, setForm] = useState<PropertyInput>({
    listing_type: 'buy',
    city: 'Gurgaon',
    sector: 'Sector 56',
    prop_type: 'Apartment',
    area: 1200,
    bedrooms: 2,
    bathrooms: 2,
    furnishing_status: 'Semi-Furnished',
    legal_status: 'Freehold',
    amenities: { has_pool: false, has_gym: false, has_lift: true, has_power_backup: true, is_gated_community: true },
    location_score: { is_near_metro: false, is_corner_property: false, is_park_facing: false, is_vastu_compliant: false },
    features: { is_luxury: false, is_servant_room: false, is_study_room: false, is_store_room: false, is_pooja_room: false }
  });

  useEffect(() => {
    let active = true;
    const fetchLocs = async () => {
      setIsFetchingLocalities(true);
      const locs = await api.getLocalities(form.city);
      if (active) {
        setLocalities(locs);
        if (locs.length > 0 && !locs.includes(form.sector)) {
           setForm(f => ({ ...f, sector: locs[0] }));
        }
        setIsFetchingLocalities(false);
      }
    };
    fetchLocs();
    return () => { active = false; };
  }, [form.city]);

  useEffect(() => {
    const timer = setTimeout(() => {
      onSubmit(form);
    }, 500);
    return () => clearTimeout(timer);
  }, [form.city, form.sector, form.area, form.bedrooms]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(form);
  };

  const InputWrapper = ({ label, icon: Icon, children }: { label: string; icon?: React.ElementType; children: React.ReactNode }) => (
    <div className="flex flex-col gap-2.5 w-full">
      <label className="label-eyebrow flex items-center gap-2">
        {Icon && <Icon className="w-3.5 h-3.5 text-primary" />}
        {label}
      </label>
      {children}
    </div>
  );

  return (
    <form onSubmit={handleSubmit} className="institutional-card bg-white p-8 md:p-10 flex flex-col gap-8 md:gap-10">
      
      {/* Market Selector */}
      <div className="flex p-1 bg-slate-50 border border-slate-100 rounded-2xl">
        {['buy', 'rent'].map((type) => (
          <button
            key={type}
            type="button"
            onClick={() => setForm({ ...form, listing_type: type as any })}
            className={cn(
              "flex-1 py-3 text-[10px] font-black uppercase tracking-widest rounded-xl transition-all",
              form.listing_type === type 
                ? "bg-primary text-white shadow-lg shadow-primary/20" 
                : "text-slate-400 hover:text-slate-600"
            )}
          >
            {type === 'buy' ? 'Standard Market' : 'Rental Market'}
          </button>
        ))}
      </div>

      {/* Primary Data Grid */}
      <div className="flex flex-col gap-8">
        <InputWrapper label="Primary Market City" icon={MapPin}>
          <select 
            className="h-14 bg-slate-50 border-none rounded-2xl px-5 text-base font-black uppercase tracking-widest text-slate-900 focus:ring-2 focus:ring-primary/20 outline-none transition-all cursor-pointer"
            value={form.city}
            onChange={(e) => setForm({...form, city: e.target.value})}
          >
            {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </InputWrapper>

        <InputWrapper label="Property Locality" icon={MapPin}>
          <select 
            className="h-14 bg-slate-50 border-none rounded-2xl px-5 text-base font-black uppercase tracking-widest text-slate-900 focus:ring-2 focus:ring-primary/20 outline-none transition-all disabled:opacity-50 cursor-pointer"
            value={form.sector}
            onChange={(e) => setForm({...form, sector: e.target.value})}
            disabled={isFetchingLocalities || localities.length === 0}
          >
            {localities.length === 0 && <option value={form.sector}>{form.sector}</option>}
            {localities.map(l => <option key={l} value={l}>{l}</option>)}
          </select>
        </InputWrapper>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <InputWrapper label="Asset Class" icon={Home}>
            <select 
              className="h-14 bg-slate-50 border-none rounded-2xl px-5 text-base font-black uppercase tracking-widest text-slate-900 focus:ring-2 focus:ring-primary/20 outline-none transition-all cursor-pointer"
              value={form.prop_type}
              onChange={(e) => setForm({...form, prop_type: e.target.value as PropertyInput['prop_type']})}
            >
              {PROPERTY_TYPES.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </InputWrapper>

          <InputWrapper label="BHK Configuration" icon={Home}>
            <select 
              className="h-14 bg-slate-50 border-none rounded-2xl px-5 text-base font-black uppercase tracking-widest text-slate-900 focus:ring-2 focus:ring-primary/20 outline-none transition-all cursor-pointer"
              value={form.bedrooms}
              onChange={(e) => setForm({...form, bedrooms: Number(e.target.value)})}
            >
              {BHK_OPTIONS.map(b => <option key={b} value={b}>{b}</option>)}
            </select>
          </InputWrapper>
        </div>

        <InputWrapper label="Total Floor Area (sqft)" icon={Ruler}>
          <input 
            type="number"
            className="h-14 bg-slate-50 border-none rounded-2xl px-5 text-base font-black tracking-tighter text-slate-900 focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            value={form.area}
            onChange={(e) => setForm({...form, area: Number(e.target.value)})}
          />
        </InputWrapper>
      </div>

      {/* Advanced Options Bar */}
      <div className="border border-slate-100 rounded-2xl overflow-hidden mt-2 bg-slate-50/30">
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="w-full h-14 flex items-center justify-between px-5 hover:bg-slate-50 transition-colors"
        >
          <span className="label-eyebrow flex items-center gap-3">
            <Filter className={cn("w-4 h-4", showAdvanced ? "text-primary" : "text-slate-300")} /> 
            Refinement Variables
          </span>
          {showAdvanced ? <ChevronUp className="w-4 h-4 text-slate-300" /> : <ChevronDown className="w-4 h-4 text-slate-300" />}
        </button>
        
        {showAdvanced && (
          <div className="p-8 grid grid-cols-1 gap-10 bg-white border-t border-slate-100 animate-in slide-in-from-top-2 duration-300">
            <div className="flex flex-col gap-5">
              <span className="label-eyebrow text-slate-300">Premium Amenities</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                {Object.entries(form.amenities).map(([key, val]) => (
                  <label key={key} className="flex items-center gap-4 cursor-pointer group min-h-[32px]">
                    <div className="relative flex items-center">
                      <input 
                        type="checkbox" 
                        checked={val} 
                        onChange={(e) => setForm({...form, amenities: {...form.amenities, [key]: e.target.checked}})}
                        className="accent-primary w-5 h-5 rounded-md"
                      />
                    </div>
                    <span className="text-[12px] font-black uppercase tracking-widest text-slate-600 group-hover:text-primary transition-colors">
                      {key.replace('has_', '').replace('is_', '').replace(/_/g, ' ')}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div className="flex flex-col gap-5">
              <span className="label-eyebrow text-slate-300">Spatial Factors</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                {Object.entries(form.location_score).map(([key, val]) => (
                  <label key={key} className="flex items-center gap-4 cursor-pointer group min-h-[32px]">
                    <div className="relative flex items-center">
                      <input 
                        type="checkbox" 
                        checked={val} 
                        onChange={(e) => setForm({...form, location_score: {...form.location_score, [key]: e.target.checked}})}
                        className="accent-primary w-5 h-5 rounded-md"
                      />
                    </div>
                    <span className="text-[12px] font-black uppercase tracking-widest text-slate-600 group-hover:text-primary transition-colors">
                      {key.replace('is_', '').replace(/_/g, ' ')}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Dual-Mode Submit: Sticky on Mobile, Static on Desktop */}
      <div className="fixed inset-x-0 bottom-0 p-6 bg-white/80 backdrop-blur-xl border-t border-slate-100 lg:static lg:p-0 lg:bg-transparent lg:border-none z-50">
        <button 
          type="submit" 
          disabled={isLoading}
          className="btn-premium w-full shadow-primary/20 text-base"
        >
          {isLoading ? (
            <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <>Calibrate Market Valuation <BarChart3 className="w-5 h-5" /></>
          )}
        </button>
      </div>

      {/* Spacing for sticky mobile button */}
      <div className="h-24 lg:hidden" />

    </form>
  );
}
