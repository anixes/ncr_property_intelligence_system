'use client';

import React from 'react';
import { LucideIcon, X } from 'lucide-react';
import * as Slider from '@radix-ui/react-slider';
import { InstitutionalSelect } from './InstitutionalSelect';

interface InputPorterProps {
  label: string;
  value: any;
  onChange: (v: any) => void;
  icon?: LucideIcon;
  type?: 'text' | 'number' | 'select' | 'autocomplete' | 'multi-select' | 'presets' | 'range' | 'segmented';
  options?: string[] | { label: string; value: any }[];
  suggestions?: string[];
  min?: number;
  max?: number;
  step?: number;
  placeholder?: string;
  className?: string;
}

export const InputPorter = ({ 
  label, 
  value, 
  onChange, 
  icon: Icon, 
  type = 'text', 
  options = [], 
  suggestions = [],
  min,
  max,
  step,
  placeholder,
  className = ""
}: InputPorterProps) => {
  
  const removeMultiValue = (valToRemove: string) => {
    if (Array.isArray(value)) {
      onChange(value.filter(v => v !== valToRemove));
    }
  };

  return (
    <div className={`space-y-2 sm:space-y-4 group transition-all duration-500 ${className}`}>
      <div className="flex items-center justify-between gap-3">
         <div className="flex items-center gap-2">
            {Icon && <Icon className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-primary/30 group-focus-within:text-primary transition-colors" />}
            <span className="text-[9px] sm:text-[10px] font-black uppercase tracking-[0.2em] sm:tracking-[0.4em] text-[#adaaab] font-body blur-[0.2px]">{label}</span>
         </div>
         {type === 'range' && (
            <span className="text-[9px] font-black text-primary/60 font-mono">
              {Array.isArray(value) ? `${value[0]} - ${value[1]}` : value}
            </span>
         )}
      </div>
      
      {type === 'select' ? (
        <InstitutionalSelect 
          value={value}
          onChange={onChange}
          options={options as string[]}
          placeholder={placeholder || `Select ${label}`}
        />
      ) : type === 'segmented' ? (
        <div className="flex flex-wrap sm:flex-nowrap bg-white/[0.02] border border-white/5 rounded-xl p-1 gap-1">
          {(options as string[]).map((opt) => {
            const isActive = Array.isArray(value) ? value.includes(opt) : value === opt;
            return (
              <button
                key={opt}
                onClick={() => {
                  if (Array.isArray(value)) {
                    if (value.includes(opt)) onChange(value.filter(v => v !== opt));
                    else onChange([...value, opt]);
                  } else {
                    onChange(opt);
                  }
                }}
                className={`flex-1 px-2 py-2 min-h-[36px] rounded-lg text-[9px] font-black uppercase tracking-wider transition-all active:scale-95 whitespace-nowrap ${
                  isActive 
                    ? 'bg-primary text-black shadow-[0_0_15px_rgba(189,157,255,0.2)]' 
                    : 'text-[#adaaab] hover:text-white hover:bg-white/5'
                }`}
              >
                {opt}
              </button>
            );
          })}
        </div>
      ) : type === 'multi-select' ? (
        <div className="relative space-y-2">
          <InstitutionalSelect 
            value="" 
            onChange={(val) => {
              if (Array.isArray(value)) {
                if (!value.includes(val)) onChange([...value, val]);
              } else {
                onChange([val]);
              }
            }}
            options={(options as string[]).filter(opt => !((value as string[]) || []).includes(opt))}
            placeholder={placeholder || `Add ${label}`}
          />
          {Array.isArray(value) && value.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {value.map((v) => (
                <button
                  key={v}
                  onClick={() => removeMultiValue(v)}
                  className="flex items-center gap-1.5 px-3 py-1.5 min-h-[32px] rounded-lg bg-primary/10 border border-primary/20 text-primary hover:bg-primary/20 active:scale-95 transition-all group/tag"
                >
                  <span className="text-[9px] font-black uppercase tracking-tight">{v}</span>
                  <X className="w-3 h-3 opacity-50 group-hover/tag:opacity-100 transition-opacity" />
                </button>
              ))}
            </div>
          )}
        </div>
      ) : type === 'autocomplete' ? (
        <div className="relative">
          <input 
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            className="w-full bg-white/[0.03] border border-white/5 rounded-xl sm:rounded-2xl px-4 py-3 sm:p-5 text-xs sm:text-base font-black font-headline text-white transition-all focus:bg-white/[0.07] focus:border-primary/30 outline-none min-h-[48px] sm:min-h-[56px]"
            list={`${label.replace(/\s+/g, '-').toLowerCase()}-list`}
          />
          <datalist id={`${label.replace(/\s+/g, '-').toLowerCase()}-list`}>
            {(suggestions || []).map((s: string) => <option key={s} value={s} />)}
          </datalist>
        </div>
      ) : type === 'presets' ? (
        <div className="flex flex-wrap gap-2">
           {((options as { label: string; value: any }[]) || []).map((opt) => {
              const isActive = value === opt.value;
              return (
                <button
                  key={String(opt.value)}
                  onClick={() => onChange(opt.value)}
                  className={`px-4 py-2.5 rounded-xl border text-[9px] font-black uppercase tracking-widest transition-all active:scale-95 whitespace-nowrap min-h-[36px] ${
                    isActive 
                      ? 'bg-primary text-black border-primary shadow-[0_0_20px_rgba(189,157,255,0.3)]' 
                      : 'bg-white/[0.03] border-white/5 text-[#adaaab] hover:border-white/10 hover:text-white'
                  }`}
                >
                  {opt.label}
                </button>
              );
           })}
        </div>
      ) : type === 'range' ? (
        <div className="space-y-4 pt-1 min-h-[48px] sm:min-h-[56px] flex flex-col justify-center">
          <Slider.Root
            className="relative flex items-center select-none touch-none w-full h-5"
            value={Array.isArray(value) ? value : [value]}
            onValueChange={(v) => onChange(Array.isArray(value) ? v : v[0])}
            max={max}
            min={min}
            step={step}
          >
            <Slider.Track className="bg-white/5 relative grow rounded-full h-[4px] sm:h-[6px]">
              <Slider.Range className="absolute bg-gradient-to-r from-primary/50 to-primary rounded-full h-full" />
            </Slider.Track>
            <Slider.Thumb
              className="block w-5 h-5 sm:w-6 sm:h-6 bg-white border-2 border-primary rounded-full shadow-[0_0_15px_rgba(189,157,255,0.4)] hover:shadow-[0_0_20px_rgba(189,157,255,0.6)] hover:scale-110 active:scale-95 transition-all outline-none cursor-pointer z-20"
              aria-label="Thumb 1"
            />
            {Array.isArray(value) && (
              <Slider.Thumb
                className="block w-5 h-5 sm:w-6 sm:h-6 bg-white border-2 border-primary rounded-full shadow-[0_0_15px_rgba(189,157,255,0.4)] hover:shadow-[0_0_20px_rgba(189,157,255,0.6)] hover:scale-110 active:scale-95 transition-all outline-none cursor-pointer z-20"
                aria-label="Thumb 2"
              />
            )}
          </Slider.Root>
          <div className="flex justify-between items-center px-1">
             <span className="text-[9px] font-black text-white/40 font-mono uppercase tracking-tighter">{placeholder?.split('-')[0]}</span>
             <span className="text-[9px] font-black text-white/40 font-mono uppercase tracking-tighter">{placeholder?.split('-')[1]}</span>
          </div>
        </div>
      ) : (
        <input 
          type={type}
          value={value}
          onChange={(e) => onChange(type === 'number' ? Number(e.target.value) : e.target.value)}
          placeholder={placeholder}
          className="w-full bg-white/[0.03] border border-white/5 rounded-xl sm:rounded-2xl px-4 py-3 sm:p-5 text-xs sm:text-base font-black font-headline text-white transition-all focus:bg-white/[0.07] focus:border-primary/30 outline-none min-h-[48px] sm:min-h-[56px]"
        />
      )}
    </div>
  );
};

interface ToggleProps {
  label: string;
  active: boolean;
  onClick: () => void;
  icon?: LucideIcon;
  sublabel?: string;
  className?: string;
}

export const Toggle = ({ label, active, onClick, icon: Icon, sublabel, className = "" }: ToggleProps) => (
  <button 
    onClick={onClick}
    className={`flex items-center justify-between px-3 py-2.5 sm:px-5 sm:py-3.5 min-h-[44px] sm:min-h-[52px] rounded-xl border transition-all active:scale-[0.97] ${className} ${
      active 
        ? 'bg-primary/10 border-primary/30 text-white shadow-[0_0_20px_rgba(189,157,255,0.1)]' 
        : 'bg-white/[0.02] border-white/5 text-[#adaaab] hover:border-white/10'
    }`}
  >
    <div className="flex items-center gap-2 sm:gap-2.5">
       {Icon && <Icon className={`w-3 h-3 sm:w-3.5 sm:h-3.5 ${active ? 'text-primary' : 'text-[#adaaab]/40'}`} />}
       <div className="flex flex-col items-start gap-0">
          <span className="text-[8.5px] sm:text-[9px] font-black uppercase tracking-widest leading-none sm:leading-tight">{label}</span>
          {sublabel && <span className="text-[7.5px] sm:text-[8px] font-medium opacity-40 uppercase tracking-tighter truncate max-w-[80px] sm:max-w-none">{sublabel}</span>}
       </div>
    </div>
    <div className={`w-1 w-1 rounded-full flex-shrink-0 ${active ? 'bg-primary shadow-[0_0_8px_rgba(189,157,255,0.8)]' : 'bg-white/10'}`} />
  </button>
);

interface PropertyCommandCardProps {
  title: string;
  children: React.ReactNode;
  icon?: LucideIcon;
  className?: string;
}

export const PropertyCommandCard = ({ title, children, icon: Icon, className = "" }: PropertyCommandCardProps) => (
  <div className={`bg-white/[0.01] border border-white/5 rounded-2xl p-4 sm:p-10 space-y-4 sm:space-y-8 flex flex-col hover:border-white/10 transition-colors ${className}`}>
     <div className="flex items-center gap-3 sm:gap-4">
        <div className="w-7 h-7 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-white/5 flex items-center justify-center text-primary/60">
           {Icon && <Icon className="w-3.5 h-3.5 sm:w-5 sm:h-5" />}
        </div>
        <h5 className="text-[8.5px] sm:text-[10px] font-black text-white uppercase tracking-[0.2em]">{title}</h5>
     </div>
     <div className="flex-1">
        {children}
     </div>
  </div>
);
