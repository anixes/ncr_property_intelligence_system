'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BarChart3, Compass } from 'lucide-react';

export default function NavShell() {
  const [scrolled, setScrolled] = useState(false);
  const pathname = usePathname();
  const isHome = pathname === '/';

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Estimator', href: '/dashboard', icon: BarChart3 },
    { name: 'Search', href: '/discovery', icon: Compass },
  ];

  return (
    <nav className={`fixed top-0 left-0 right-0 z-[100] transition-all duration-700 h-20 flex items-center ${
      scrolled ? 'bg-[#0e0e0f]/90 backdrop-blur-3xl border-b border-white/5' : 'bg-transparent'
    }`}>
      <div className="w-full max-w-[1400px] mx-auto px-5 sm:px-10 flex items-center justify-between">

        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 group transition-all duration-300 active:scale-95">
          <div className="relative w-9 h-9 flex items-center justify-center">
            <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping opacity-20" />
            <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/40 flex items-center justify-center group-hover:bg-primary/20 transition-all duration-500">
              <div className="w-3 h-3 rounded-full bg-primary shadow-[0_0_15px_#bd9dff]" />
            </div>
          </div>
          <div className="flex flex-col -space-y-0.5">
            <span className="font-headline font-black tracking-tightest text-base sm:text-xl uppercase text-white leading-none">NCR Intel</span>
            <span className="text-[9px] font-black tracking-[0.4em] uppercase text-primary/60">Platform</span>
          </div>
        </Link>

        {/* Nav Links — always visible, compact pills */}
        <div className="flex items-center gap-2">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            const Icon = link.icon;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-2 px-3 sm:px-6 py-2.5 rounded-xl transition-all duration-300 min-h-[44px] sm:min-h-[48px] ${
                  isActive
                    ? 'bg-primary/15 border border-primary/30 text-primary shadow-[0_0_20px_rgba(189,157,255,0.1)]'
                    : 'border border-white/10 text-white/40 hover:text-white hover:border-white/20 bg-white/[0.03] active:scale-95'
                }`}
              >
                <Icon size={16} className="flex-shrink-0" />
                <span className="hidden xs:block text-[9px] sm:text-[10px] font-black uppercase tracking-[0.2em]">{link.name}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
