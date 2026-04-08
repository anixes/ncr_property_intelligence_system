'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Check } from 'lucide-react';

interface Props {
  label?: string;
  value: string;
  options: string[];
  onChange: (value: string) => void;
  icon?: any;
  className?: string;
  placeholder?: string;
}

export const InstitutionalSelect = ({ 
  label, 
  value, 
  options = [], 
  onChange, 
  icon: Icon,
  className = "",
  placeholder = "Select Option"
}: Props) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);

  const filteredOptions = (options || []).filter(opt => 
    String(opt).toLowerCase().includes((searchQuery || "").toLowerCase())
  );

  // Reset search when closing
  useEffect(() => {
    if (!isOpen) setSearchQuery("");
  }, [isOpen]);

  // Close on click outside
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  return (
    <div className={`relative ${className}`} ref={containerRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full bg-white/[0.03] border border-white/5 rounded-xl sm:rounded-2xl p-3 sm:p-5 pr-10 sm:pr-12 text-left transition-all hover:bg-white/[0.07] focus:border-primary/30 outline-none flex items-center justify-between group min-h-[48px] sm:min-h-[56px]"
      >
        <div className="flex flex-col gap-0">
          {label && (
            <span className="text-[9px] sm:text-[10px] font-black uppercase tracking-[0.2em] sm:tracking-[0.3em] text-[#adaaab] mb-0.5 group-hover:text-primary/60 transition-colors">
              {label}
            </span>
          )}
          <span className={`text-xs sm:text-base font-black font-headline tracking-tight antialiased [text-rendering:optimizeLegibility] ${value ? 'text-white' : 'text-white/20'}`}>
            {value || placeholder}
          </span>
        </div>
        
        <div className={`absolute right-4 sm:right-5 top-1/2 -translate-y-1/2 transition-transform duration-300 ${isOpen ? 'rotate-180 text-primary' : 'text-white/20'}`}>
          <ChevronDown className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
        </div>
      </button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0, y: 10, scale: 0.95 }}
              animate={{ opacity: 1, y: 5, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.95 }}
              transition={{ type: "spring", damping: 25, stiffness: 300, duration: 0.2 }}
              className="absolute z-[150] w-full mt-2 bg-[#1a1a1c]/95 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden"
            >
              
              <div className="max-h-[60vh] sm:max-h-[400px] flex flex-col pb-8 sm:pb-0">
                {/* Search Header (Only show for high-density lists) */}
                {options.length > 10 && (
                  <div className="px-4 py-3 border-b border-white/5 sticky top-0 bg-[#1a1a1c] z-10">
                     <div className="relative">
                        <input 
                          type="text"
                          placeholder="Search"
                          className="w-full bg-white/[0.03] border border-white/5 rounded-lg px-3 py-2 text-[10px] font-black uppercase tracking-widest text-white outline-none focus:border-primary/40 transition-all"
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                        />
                     </div>
                  </div>
                )}

                <div className="flex-1 overflow-y-auto overscroll-contain">
                  {filteredOptions.length === 0 ? (
                    <div className="p-8 text-center text-[10px] font-black uppercase tracking-widest text-white/20 italic">
                      No matching sectors
                    </div>
                  ) : (
                    filteredOptions.map((opt) => (
                    <button
                      key={opt}
                      onClick={() => {
                        onChange(opt);
                        setIsOpen(false);
                      }}
                      className={`w-full px-6 py-4 sm:py-3 min-h-[56px] sm:min-h-[48px] text-left flex items-center justify-between group transition-all ${
                        value === opt ? 'bg-primary/10 text-primary' : 'text-[#adaaab] hover:bg-white/5 hover:text-white'
                      }`}
                    >
                      <span className="text-[10px] sm:text-xs font-black font-headline tracking-widest uppercase">
                        {opt}
                      </span>
                      {value === opt && (
                        <Check className="w-4 h-4 text-primary animate-in zoom-in duration-300" />
                      )}
                    </button>
                  ))
                )}
              </div>
            </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
