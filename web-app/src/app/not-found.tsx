import { Compass, Search, BarChart3, Home } from 'lucide-react';
import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-[85vh] flex items-center justify-center p-6 lg:p-12">
      <div className="max-w-2xl w-full">
        <div className="institutional-card bg-white p-12 md:p-16 flex flex-col items-center text-center relative overflow-hidden">
          
          {/* Signal Indicator */}
          <div className="absolute top-0 inset-x-0 h-1 bg-slate-900" />
          
          <div className="w-20 h-20 bg-slate-50 rounded-3xl flex items-center justify-center mb-10 shadow-lg shadow-slate-900/5 border border-slate-100">
            <Compass className="w-10 h-10 text-slate-400 animate-[spin_10s_linear_infinite]" />
          </div>

          <h1 className="text-3xl md:text-4xl font-black text-slate-900 uppercase tracking-tighter mb-6">
            Spatial Identifier Not Found
          </h1>
          
          <p className="text-slate-500 font-bold leading-relaxed mb-12 max-w-sm">
            The requested asset coordinate or tactical route is outside of our currently archived intelligence grid.
          </p>

          <div className="flex flex-col gap-4 w-full">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Link
                href="/analyzer"
                className="btn-premium h-14 text-sm flex items-center justify-center gap-3"
              >
                <BarChart3 className="w-4 h-4" /> Market Analyzer
              </Link>
              <Link
                href="/discover"
                className="flex items-center justify-center gap-3 h-14 bg-white border border-slate-100 rounded-2xl text-[11px] font-black uppercase tracking-widest text-slate-600 hover:border-primary/20 hover:text-primary transition-all shadow-sm"
              >
                <Search className="w-4 h-4" /> Discover Assets
              </Link>
            </div>
            
            <Link
              href="/"
              className="flex items-center justify-center gap-3 h-14 bg-slate-50 border border-slate-100 rounded-2xl text-[11px] font-black uppercase tracking-widest text-slate-400 hover:bg-white hover:text-primary hover:border-primary/20 transition-all"
            >
              <Home className="w-4 h-4" /> Return to Terminal Home
            </Link>
          </div>

          <div className="mt-12 pt-10 border-t border-slate-50 w-full">
             <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-300">
                Institutional Precision © 2026
             </p>
          </div>
        </div>
      </div>
    </div>
  );
}
