import { Building2 } from 'lucide-react';
import Link from 'next/link';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-background border-t border-white/[0.05] mt-auto relative z-10">
      <div className="max-w-[1800px] mx-auto px-6 py-24">
        <div className="grid grid-cols-1 md:grid-cols-[2fr_1fr_1fr_1fr] gap-24 mb-24">
          
          <div className="flex flex-col gap-8">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary rounded-lg shadow-lg shadow-primary/40 flex items-center justify-center">
                <Building2 className="w-4 h-4 text-white" />
              </div>
              <span className="text-sm font-black tracking-[0.2em] text-white uppercase">
                NCR Intelligence
              </span>
            </div>
            <p className="text-[10px] text-white/40 font-black uppercase tracking-widest leading-relaxed max-w-xs">
              Institutional-grade property intelligence and valuation accuracy for the National Capital Region. Precision engineering for real estate markets.
            </p>
          </div>

          {[
            { t: 'Platform', l: [{n:'Portfolio', h:'/dashboard'}, {n:'Analysis', h:'/analyzer'}, {n:'Acquisitions', h:'/discover'}] },
            { t: 'Intelligence', l: [{n:'Methodology', h:'#'}, {n:'Data Index', h:'#'}, {n:'Market Pulse', h:'#'}] },
            { t: 'Corporate', l: [{n:'Contact', h:'#'}, {n:'Security', h:'#'}, {n:'Terms', h:'#'}] }
          ].map((cat, i) => (
            <div key={i} className="flex flex-col gap-8">
              <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-white/20">{cat.t}</h4>
              <div className="flex flex-col gap-4">
                {cat.l.map(link => (
                  <Link key={link.n} href={link.h} className="text-[10px] font-black text-white/40 uppercase tracking-widest hover:text-white transition-colors">{link.n}</Link>
                ))}
              </div>
            </div>
          ))}

        </div>

        <div className="pt-12 border-t border-white/[0.05] flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="text-[9px] font-black uppercase tracking-[0.3em] text-white/20">
            &copy; {currentYear} Institutional Real Estate Registry. All Rights Reserved.
          </div>
          <div className="flex items-center gap-12">
             <span className="text-[9px] font-black uppercase tracking-[0.3em] text-white/20">NCR Core Connect</span>
             <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse shadow-[0_0_10px_rgba(91,19,236,0.6)]" />
          </div>
        </div>
      </div>
    </footer>
  );
}

