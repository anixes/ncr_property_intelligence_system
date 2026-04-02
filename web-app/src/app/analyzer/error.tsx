'use client';

import { useEffect } from 'react';
import { AlertCircle, RefreshCcw, Home } from 'lucide-react';
import Link from 'next/link';

export default function AnalyzerError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log analytical failure to institutional monitoring
    console.error('Mathematical Engine Error:', error);
  }, [error]);

  return (
    <div className="flex-1 w-full min-h-screen bg-slate-50/50 flex items-center justify-center p-6 lg:p-8">
      <div className="institutional-card bg-white p-12 max-w-xl w-full flex flex-col items-center text-center gap-8 shadow-2xl">
        <div className="p-4 bg-red-50 text-red-600 rounded-[28px] shadow-sm border border-red-100">
          <AlertCircle className="w-8 h-8" />
        </div>

        <div className="flex flex-col gap-3">
          <span className="label-eyebrow text-red-500">Processing Interrupted</span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tighter uppercase">
            Analytical Engine Timeout
          </h1>
          <p className="text-slate-500 font-medium text-sm leading-relaxed">
            The market volatility vectors for your selected locality are currently 
            re-indexing. Our mathematical engine could not establish a precise valuation.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 w-full">
          <button
            onClick={() => reset()}
            className="btn-premium flex-1 flex items-center justify-center gap-3 shadow-primary/20"
          >
            <RefreshCcw className="w-4 h-4" /> Re-Initialize Engine
          </button>
          
          <Link 
            href="/"
            className="flex-1 h-14 rounded-2xl border border-slate-100 flex items-center justify-center gap-3 text-[11px] font-black uppercase tracking-widest text-slate-400 hover:bg-slate-50 hover:text-slate-600 transition-all"
          >
            <Home className="w-4 h-4" /> Return to Terminal
          </Link>
        </div>

        <div className="pt-6 border-t border-slate-50 w-full text-[10px] font-black text-slate-300 uppercase tracking-widest">
          Ref ID: {error.digest || 'ANALYTICS-FAIL-01'}
        </div>
      </div>
    </div>
  );
}
