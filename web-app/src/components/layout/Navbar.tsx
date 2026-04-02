'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Building2, Search, BarChart3, Bookmark, Bell, Grid } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { useShortlist } from '@/hooks/useShortlist';
import MobileNavClient from './MobileNavClient';

const navItems = [
  { name: 'Portfolio', href: '/dashboard', icon: BarChart3 },
  { name: 'Analysis', href: '/analyzer', icon: BarChart3 },
  { name: 'Acquisitions', href: '/discover', icon: Search },
];

export default function Navbar() {
  const pathname = usePathname();
  const { shortlist } = useShortlist();
  const [health, setHealth] = useState<'loading' | 'online' | 'error'>('loading');

  useEffect(() => {
    api.getHealth()
      .then(() => setHealth('online'))
      .catch(() => setHealth('error'));
  }, []);

  return (
    <nav className="fixed top-0 left-0 right-0 z-[200] border-b border-white/[0.05] bg-background/40 backdrop-blur-3xl">
      <div className="max-w-[1800px] mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-12">
          <Link href="/" className="flex items-center gap-3 active:scale-95 transition-all">
            <div className="w-8 h-8 bg-primary rounded-lg shadow-lg shadow-primary/40 flex items-center justify-center">
              <Building2 className="w-4 h-4 text-white" />
            </div>
            <span className="font-black text-[12px] tracking-[0.2em] text-white uppercase hidden lg:block">
              NCR <span className="text-primary">Intelligence</span>
            </span>
          </Link>

          <div className="hidden lg:flex items-center gap-4">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "px-5 py-2 rounded-full text-[10px] font-black uppercase tracking-widest transition-all duration-300",
                  pathname.startsWith(item.href)
                    ? "text-white bg-primary/20 border border-primary/20"
                    : "text-white/40 hover:text-white"
                )}
              >
                {item.name}
              </Link>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-6">
          {/* Status HUD Chips */}
          <div className="hidden lg:flex items-center gap-3">
            {shortlist.length > 0 && (
              <div className="flex items-center gap-2.5 px-3 py-1.5 bg-white/5 border border-white/5 rounded-full backdrop-blur-md">
                <Bookmark className="w-3 h-3 text-primary fill-primary" />
                <span className="text-white/60 text-[9px] font-black uppercase tracking-[0.1em]">
                  {shortlist.length} Assets
                </span>
              </div>
            )}
            
            <div className="flex items-center gap-2.5 px-3 py-1.5 bg-white/5 border border-white/5 rounded-full backdrop-blur-md">
              <div className={cn(
                "w-1 h-1 rounded-full",
                health === 'online' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-400'
              )} />
              <span className="text-white/60 text-[9px] font-black uppercase tracking-[0.1em]">
                {health === 'online' ? 'Live Node' : 'Syncing Engine'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3 border-l border-white/10 pl-6 h-8">
            <button className="text-white/40 hover:text-white transition-colors">
               <Bell className="w-4 h-4" />
            </button>
            <div className="lg:hidden">
              <MobileNavClient shortlistCount={shortlist.length} health={health} />
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

