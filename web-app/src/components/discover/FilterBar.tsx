'use client';

import { useState, useEffect } from 'react';
import { MapPin, Calculator, Home, ArrowRight, Filter } from 'lucide-react';
import { DiscoverRequest } from '@/types';
import { cn } from '@/lib/utils';

interface FilterBarProps {
  onSearch: (filters: DiscoverRequest) => void;
  isLoading: boolean;
  initialFilters: DiscoverRequest;
}

const CITIES = ['Gurgaon', 'Noida', 'Delhi', 'Greater Noida'];

export default function FilterBar({ onSearch, isLoading, initialFilters }: FilterBarProps) {
  const [filters, setFilters] = useState<DiscoverRequest>(initialFilters);

  useEffect(() => {
    setFilters(initialFilters);
  }, [initialFilters]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(filters);
  };

  return (
    <div className="max-w-[1400px] mx-auto sticky top-20 z-40">
      <form 
        onSubmit={handleSubmit}
        className="institutional-card bg-white p-6 md:p-8"
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 lg:gap-8">
          
          {/* City / Locality */}
          <div className="flex flex-col gap-2.5">
            <label className="label-eyebrow flex items-center gap-2">
              <MapPin className="w-3 h-3" /> Target Market
            </label>
            <select 
              value={filters.city}
              onChange={(e) => setFilters({ ...filters, city: e.target.value })}
              className="h-12 bg-slate-50 border-none rounded-xl px-4 text-base font-black uppercase tracking-widest text-slate-900 focus:ring-2 focus:ring-primary/20 cursor-pointer"
            >
              {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          {/* Type */}
          <div className="flex flex-col gap-2.5">
            <label className="label-eyebrow flex items-center gap-2">
              <Home className="w-3 h-3" /> Asset Type
            </label>
            <div className="flex bg-slate-50 p-1 rounded-xl h-12">
              {['buy', 'rent'].map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setFilters({ ...filters, listing_type: type as any })}
                  className={cn(
                    "flex-1 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all",
                    filters.listing_type === type 
                      ? "bg-white text-primary shadow-sm" 
                      : "text-slate-400 hover:text-slate-600"
                  )}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {/* BHK Range */}
          <div className="flex flex-col gap-2.5">
            <label className="label-eyebrow flex items-center gap-2">
              <Filter className="w-3 h-3" /> Configuration
            </label>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((num) => (
                <button
                  key={num}
                  type="button"
                  onClick={() => {
                    const next = filters.bhk.includes(num) 
                      ? filters.bhk.filter(b => b !== num)
                      : [...filters.bhk, num].sort();
                    if (next.length > 0) setFilters({ ...filters, bhk: next });
                  }}
                  className={cn(
                    "w-11 h-11 rounded-xl flex items-center justify-center text-base font-black transition-all border",
                    filters.bhk.includes(num)
                      ? "bg-primary border-primary text-white shadow-lg shadow-primary/20"
                      : "bg-white border-slate-100 text-slate-400 hover:border-primary/20"
                  )}
                >
                  {num}
                </button>
              ))}
            </div>
          </div>

          {/* Budget */}
          <div className="flex flex-col gap-2.5 sm:col-span-1 md:col-span-2 lg:col-span-1">
            <label className="label-eyebrow flex items-center gap-2">
              <Calculator className="w-3 h-3" /> Budget (Lakhs)
            </label>
            <div className="flex items-center gap-3">
              <input 
                type="number"
                value={filters.budget_min}
                onChange={(e) => setFilters({ ...filters, budget_min: Number(e.target.value) })}
                className="w-full h-12 bg-slate-50 border-none rounded-xl px-4 text-base font-black text-slate-900 focus:ring-2 focus:ring-primary/20"
                placeholder="Min"
              />
              <span className="text-slate-300 font-black">-</span>
              <input 
                type="number"
                value={filters.budget_max}
                onChange={(e) => setFilters({ ...filters, budget_max: Number(e.target.value) })}
                className="w-full h-12 bg-slate-50 border-none rounded-xl px-4 text-base font-black text-slate-900 focus:ring-2 focus:ring-primary/20"
                placeholder="Max"
              />
            </div>
          </div>

          {/* Action */}
          <div className="flex items-end col-span-1 sm:col-span-2 md:col-span-4 lg:col-span-1">
            <button 
              type="submit"
              disabled={isLoading}
              className="btn-premium w-full shadow-primary/10"
            >
              {isLoading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>Refresh Engine <ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </div>

        </div>
      </form>
    </div>
  );
}
