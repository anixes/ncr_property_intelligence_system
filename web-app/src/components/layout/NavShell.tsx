'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, Home, Compass, BarChart3, Info, ChevronRight } from 'lucide-react';

export default function NavShell() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Intelligence Dashboard', href: '/dashboard', icon: BarChart3, desc: 'Real-time asset analysis' },
    { name: 'Market Discovery', href: '/discovery', icon: Compass, desc: 'Spatial yield heatmaps' },
    { name: 'Methodology', href: '/methodology', icon: Info, desc: 'Institutional data standards' }
  ];

  return (
    <>
      <nav className={`fixed top-0 left-0 right-0 z-[100] transition-all duration-700 ${
        scrolled ? 'bg-background/40 backdrop-blur-3xl border-b border-white/5 py-3' : 'bg-transparent border-transparent py-6 sm:py-8'
      }`}>
        <div className="max-w-[1400px] mx-auto px-6 sm:px-10 flex items-center justify-between">
          
          {/* Logo: Institutional Branding */}
          <Link href="/" className="flex items-center gap-3 group transition-all duration-300 active:scale-95">
            <div className="relative w-10 h-10 flex items-center justify-center">
              <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping opacity-20" />
              <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/40 flex items-center justify-center group-hover:bg-primary/20 transition-all duration-500">
                <div className="w-3 h-3 rounded-full bg-primary text-glow-primary shadow-[0_0_15px_#bd9dff]" />
              </div>
            </div>
            <div className="flex flex-col -space-y-1">
              <span className="font-headline font-black tracking-tightest text-xl uppercase text-white">NCR Intel</span>
              <span className="text-[10px] font-black tracking-[0.4em] uppercase text-primary/60">Platform</span>
            </div>
          </Link>

          {/* Desktop Nav: Refined Spacing */}
          <div className="hidden md:flex items-center gap-12">
            {navLinks.map((link) => (
              <Link 
                key={link.name} 
                href={link.href}
                className="text-[10px] font-black text-white/40 hover:text-primary uppercase tracking-[0.2em] transition-all flex items-center gap-3 group"
              >
                <link.icon size={14} className="group-hover:scale-110 transition-transform" />
                {link.name}
              </Link>
            ))}
          </div>

          {/* Mobile Toggle: Unified Command */}
          <button 
            type="button"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden w-12 h-12 flex items-center justify-center rounded-2xl glass-panel-luxe text-primary active:scale-90 transition-all shadow-xl"
            aria-label="Toggle Menu"
          >
            {isMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </nav>

      {/* Mobile Drawer Overlay: Atmospheric Decompression */}
      <AnimatePresence>
        {isMenuOpen && (
          <motion.div 
            initial={{ opacity: 0, x: '100%' }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed inset-0 z-[110] bg-[#0e0e0f]/95 backdrop-blur-3xl md:hidden overflow-hidden flex flex-col"
          >
            <div className="flex flex-col h-full mobile-decompress">
              
              <div className="flex items-center justify-between mb-16">
                 <div className="flex flex-col -space-y-1">
                    <span className="font-headline font-black tracking-tightest text-xl uppercase text-white/20">System</span>
                    <span className="text-[10px] font-black tracking-[0.4em] uppercase text-primary/20">Navigation</span>
                 </div>
                 <button 
                    onClick={() => setIsMenuOpen(false)} 
                    className="w-12 h-12 rounded-full border border-white/5 flex items-center justify-center text-white/40 hover:text-white"
                  >
                    <X size={24} />
                 </button>
              </div>

              <div className="flex flex-col gap-10">
                {navLinks.map((link, idx) => (
                  <motion.div
                    key={link.name}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 + (idx * 0.1) }}
                  >
                    <Link
                      href={link.href}
                      onClick={() => setIsMenuOpen(false)}
                      className="flex items-center justify-between group py-4"
                    >
                      <div className="flex items-center gap-8">
                        <div className="w-16 h-16 rounded-[2rem] bg-white/5 border border-white/10 flex items-center justify-center group-active:scale-90 transition-all text-white group-hover:bg-primary group-hover:text-black group-hover:shadow-[0_0_30px_rgba(189,157,255,0.4)]">
                          <link.icon size={24} />
                        </div>
                        <div className="flex flex-col">
                          <span className="text-3xl font-black text-white uppercase tracking-tightest transition-colors group-hover:text-primary leading-none mb-1">{link.name.split(' ')[1]}</span>
                          <span className="text-[10px] uppercase font-black text-white/30 tracking-[0.3em]">{link.desc}</span>
                        </div>
                      </div>
                      <ChevronRight className="text-white/10 group-hover:text-primary transition-colors" />
                    </Link>
                  </motion.div>
                ))}
              </div>

              <div className="mt-auto border-t border-white/5 pt-12">
                 <div className="flex items-center gap-4 mb-6">
                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse shadow-[0_0_10px_#bd9dff]" />
                    <span className="text-[10px] font-black text-primary uppercase tracking-[0.4em]">Engine v1.1 Active</span>
                 </div>
                 <p className="text-[10px] font-black text-white/20 uppercase tracking-[0.3em] leading-loose">
                   National Capital Region<br />
                   Institutional Data Standards © 2026
                 </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
