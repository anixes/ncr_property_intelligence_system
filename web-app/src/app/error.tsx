'use client';

import { useEffect } from 'react';
import { ShieldAlert, RefreshCcw, Home, MessageSquare } from 'lucide-react';
import Link from 'next/link';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Pro-active Institutional Logging
    console.error('SYSTEM_FAILURE_EVENT:', error);
  }, [error]);

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-6 lg:p-12">
      <div className="max-w-2xl w-full">
        <div className="institutional-card bg-white p-12 md:p-16 flex flex-col items-center text-center relative overflow-hidden">
          
          {/* Signal Indicator */}
          <div className="absolute top-0 inset-x-0 h-1 bg-amber-400" />
          
          <div className="w-20 h-20 bg-amber-50 rounded-3xl flex items-center justify-center mb-10 shadow-lg shadow-amber-900/5 border border-amber-100">
            <ShieldAlert className="w-10 h-10 text-amber-600" />
          </div>

          <h1 className="text-3xl md:text-4xl font-black text-slate-900 uppercase tracking-tighter mb-6">
            System Synchronization Interrupted
          </h1>
          
          <p className="text-slate-500 font-bold leading-relaxed mb-12 max-w-md">
            The market intelligence engine encountered an unexpected atmospheric failure. Diagnostic event <span className="font-black text-slate-900 uppercase tracking-widest text-xs px-2 py-0.5 bg-slate-100 rounded-md">ID: {error.digest || 'ERR_GLOBAL_V1'}</span> has been recorded.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
            <button
              onClick={() => reset()}
              className="btn-premium h-14 text-sm flex items-center justify-center gap-3"
            >
              <RefreshCcw className="w-4 h-4" /> Recalibrate Connection
            </button>
            <Link
              href="/"
              className="flex items-center justify-center gap-3 h-14 bg-slate-50 border border-slate-100 rounded-2xl text-[11px] font-black uppercase tracking-widest text-slate-400 hover:bg-white hover:text-primary hover:border-primary/20 transition-all shadow-sm"
            >
              <Home className="w-4 h-4" /> Return to Command
            </Link>
          </div>

          <div className="mt-12 pt-10 border-t border-slate-50 w-full flex items-center justify-center gap-6">
             <button className="flex items-center gap-2 text-[9px] font-black uppercase tracking-[0.2em] text-slate-300 hover:text-primary transition-colors">
                <MessageSquare className="w-3.5 h-3.5" /> Report Technical Anomaly
             </button>
          </div>
        </div>
      </div>
    </div>
  );
}
