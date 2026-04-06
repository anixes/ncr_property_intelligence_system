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
  const containerRef = useRef<HTMLDivElement>(null);

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

      {/* Dropdown Menu / Mobile Sheet */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop for mobile */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[140] sm:hidden"
            />
            
            <motion.div
              initial={typeof window !== 'undefined' && window.innerWidth < 640 
                ? { y: "100%" } 
                : { opacity: 0, y: 10, scale: 0.95 }
              }
              animate={typeof window !== 'undefined' && window.innerWidth < 640 
                ? { y: 0 } 
                : { opacity: 1, y: 5, scale: 1 }
              }
              exit={typeof window !== 'undefined' && window.innerWidth < 640 
                ? { y: "100%" } 
                : { opacity: 0, y: 10, scale: 0.95 }
              }
              transition={{ type: "spring", damping: 25, stiffness: 300, duration: 0.2 }}
              className={`
                z-[150] w-full bg-[#1a1a1c]/95 backdrop-blur-2xl border border-white/10 shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden
                ${typeof window !== 'undefined' && window.innerWidth < 640 
                  ? 'fixed bottom-0 left-0 rounded-t-[32px] border-b-0' 
                  : 'absolute mt-2 rounded-2xl'
                }
              `}
            >
              {/* Handle for mobile sheet */}
              <div className="w-12 h-1 bg-white/10 rounded-full mx-auto mt-3 mb-1 sm:hidden" />
              
              <div className="max-h-[60vh] sm:max-h-[300px] overflow-y-auto overscroll-contain pb-8 sm:pb-0">
                {options.length === 0 ? (
                  <div className="p-8 text-center text-[10px] font-black uppercase tracking-widest text-white/20 italic">
                    No options available
                  </div>
                ) : (
                  options.map((opt) => (
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
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
