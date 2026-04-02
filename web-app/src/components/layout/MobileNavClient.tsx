'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Menu, X, Bookmark, Search, BarChart3, Globe } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

interface MobileNavClientProps {
  shortlistCount: number;
  health: 'loading' | 'online' | 'error';
}

const navItems = [
  { name: 'Market Analyzer', href: '/analyzer', icon: BarChart3 },
  { name: 'Property Discovery', href: '/discover', icon: Search },
];

export default function MobileNavClient({ shortlistCount, health }: MobileNavClientProps) {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  return (
    <div className="lg:hidden">
      <button
        onClick={() => setIsOpen(true)}
        className="p-3 -mr-3 text-slate-600 hover:text-primary transition-colors"
        aria-label="Open Menu"
      >
        <Menu className="w-6 h-6" />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="glass-sheet-nav"
          >
            <div className="flex items-center justify-between mb-12">
              <span className="font-black text-xl tracking-tighter text-slate-900 uppercase">
                NCR <span className="text-primary">REALTY</span>
              </span>
              <button
                onClick={() => setIsOpen(false)}
                className="p-3 -mr-3 text-slate-400 hover:text-slate-900 transition-colors"
                aria-label="Close Menu"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="flex flex-col gap-8 mb-12">
              <div className="flex items-center gap-3 px-4 py-3 bg-slate-50 border border-slate-100 rounded-2xl">
                <div className={cn(
                  "w-2 h-2 rounded-full",
                  health === 'online' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-400'
                )} />
                <span className="label-eyebrow text-slate-600">
                  {health === 'online' ? 'Live Market Data' : 'Connecting Engine...'}
                </span>
              </div>

              {shortlistCount > 0 && (
                <div className="flex items-center justify-between px-6 py-4 bg-primary/5 border border-primary/10 rounded-2xl">
                  <div className="flex items-center gap-3">
                    <Bookmark className="w-4 h-4 text-primary fill-primary" />
                    <span className="label-eyebrow text-primary text-[12px]">Saved Assets</span>
                  </div>
                  <span className="font-black text-primary bg-white px-2.5 py-0.5 rounded-full text-xs shadow-sm shadow-primary/10">
                    {shortlistCount}
                  </span>
                </div>
              )}
            </div>

            <nav className="flex flex-col gap-4">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className={cn(
                    "flex items-center justify-between p-6 rounded-2xl border transition-all duration-300",
                    pathname.startsWith(item.href)
                      ? "bg-primary border-primary text-white shadow-xl shadow-primary/20"
                      : "bg-white border-slate-100 text-slate-400 hover:border-primary/20 hover:text-slate-900 shadow-sm"
                  )}
                >
                  <div className="flex items-center gap-4">
                    <item.icon className={cn("w-5 h-5", pathname.startsWith(item.href) ? "text-white" : "text-primary/40")} />
                    <span className="font-black uppercase tracking-widest text-[11px]">
                      {item.name}
                    </span>
                  </div>
                </Link>
              ))}
            </nav>

            <div className="mt-auto pt-12 border-t border-slate-100 text-center">
              <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-300">
                Institutional Precision © 2026
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
