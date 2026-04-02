export default function AnalyzerLoading() {
  return (
    <div className="min-h-screen bg-slate-50/50 pb-24">
      {/* Institutional Breadcrumb Skeleton */}
      <div className="bg-white border-b border-slate-100 px-6 lg:px-12 py-4">
        <div className="max-w-7xl mx-auto flex items-center gap-4">
          <div className="w-24 h-3 bg-slate-100 animate-pulse rounded-full" />
          <div className="w-4 h-4 rounded-full bg-slate-50 border border-slate-100" />
          <div className="w-32 h-3 bg-slate-100 animate-pulse rounded-full" />
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 lg:px-12 mt-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
          
          {/* Form Skeleton */}
          <div className="lg:col-span-5 flex flex-col gap-8">
            <div className="institutional-card bg-white p-10 flex flex-col gap-10">
              <div className="space-y-4">
                <div className="w-32 h-3 bg-slate-100 animate-pulse rounded-full" />
                <div className="w-full h-14 bg-slate-50 animate-pulse rounded-2xl" />
              </div>
              <div className="space-y-4">
                <div className="w-40 h-3 bg-slate-100 animate-pulse rounded-full" />
                <div className="w-full h-14 bg-slate-50 animate-pulse rounded-2xl" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="h-24 bg-slate-50 animate-pulse rounded-2xl" />
                <div className="h-24 bg-slate-50 animate-pulse rounded-2xl" />
              </div>
              <div className="w-full h-16 bg-slate-900/5 animate-pulse rounded-3xl" />
            </div>
          </div>

          {/* Results Skeleton (Phantom State) */}
          <div className="lg:col-span-7 flex flex-col gap-10 opacity-60 grayscale-[0.5]">
            <div className="institutional-card bg-white p-12 flex flex-col items-center justify-center min-h-[400px] border-dashed">
               <div className="w-16 h-16 rounded-full border-4 border-slate-50 border-t-slate-200 animate-spin mb-6" />
               <div className="w-48 h-3 bg-slate-100 animate-pulse rounded-full mb-3" />
               <div className="w-32 h-2 bg-slate-50 animate-pulse rounded-full" />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="h-32 bg-white/50 animate-pulse rounded-3xl border border-slate-100" />
              <div className="h-32 bg-white/50 animate-pulse rounded-3xl border border-slate-100" />
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
