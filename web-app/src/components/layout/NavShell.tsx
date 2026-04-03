'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Menu, X, Home, Compass, BarChart3, Info } from 'lucide-react';

export default function NavShell() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleMenu = (e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setIsMenuOpen(prev => !prev);
  };

  const navLinks = [
    { name: 'Intelligence Dashboard', href: '/dashboard', icon: BarChart3 },
    { name: 'Market Discovery', href: '/discovery', icon: Compass },
    { name: 'Methodology', href: '/methodology', icon: Info }
  ];

  return (
    <>
      <nav className={`fixed top-0 left-0 right-0 z-[100] transition-all duration-500 border-b ${
        scrolled ? 'bg-background/80 backdrop-blur-xl border-white/10 py-3' : 'bg-transparent border-transparent py-6'
      }`}>
        <div className="max-w-[1400px] mx-auto px-6 flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group transition-all duration-300 active:scale-95">
            <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center group-hover:bg-primary/30 transition-colors">
              <div className="w-4 h-4 rounded-full bg-primary shadow-[0_0_12px_rgba(168,143,243,0.6)]" />
            </div>
            <span className="font-manrope font-black tracking-tighter text-xl uppercase">NCR Property</span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <Link 
                key={link.name} 
                href={link.href}
                className="text-xs font-black text-white/50 hover:text-white uppercase tracking-widest transition-colors flex items-center gap-2"
              >
                {link.name}
              </Link>
            ))}
          </div>

          {/* Mobile Toggle */}
          <button 
            type="button"
            onClick={toggleMenu}
            className="md:hidden w-12 h-12 flex items-center justify-center rounded-xl bg-white/5 border border-white/10 text-white active:scale-95 transition-all"
            aria-label="Toggle Menu"
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </nav>

      {/* Mobile Drawer Overlay */}
      <div 
        className={`fixed inset-0 z-[110] transition-all duration-700 bg-background/95 backdrop-blur-3xl md:hidden ${
          isMenuOpen ? 'opacity-100 pointer-events-auto translate-x-0' : 'opacity-0 pointer-events-none translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full p-8">
          <div className="flex items-center justify-between mb-12">
             <span className="font-manrope font-black tracking-tighter text-xl uppercase opacity-40">Navigation</span>
             <button onClick={() => setIsMenuOpen(false)} className="p-2 text-white/40 hover:text-white">
                <X size={24} />
             </button>
          </div>

          <div className="flex flex-col gap-8">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                href={link.href}
                onClick={() => setIsMenuOpen(false)}
                className="flex items-center gap-6 group"
              >
                <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center group-active:scale-90 transition-all font-black text-white group-hover:bg-primary/20 group-hover:border-primary/30 group-hover:text-primary">
                  <link.icon size={24} />
                </div>
                <div className="flex flex-col">
                  <span className="text-2xl font-black text-white uppercase tracking-tighter">{link.name}</span>
                  <span className="text-[10px] uppercase font-bold text-white/30 tracking-[0.2em] transition-colors group-hover:text-primary/60">Institutional View</span>
                </div>
              </Link>
            ))}
          </div>

          <div className="mt-auto border-t border-white/5 pt-8">
             <p className="text-[10px] font-black text-white/20 uppercase tracking-widest leading-loose">
               National Capital Region<br />
               Property Intelligence Engine v1.0
             </p>
          </div>
        </div>
      </div>
    </>
  );
}
