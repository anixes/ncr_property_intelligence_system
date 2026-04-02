export default function DiscoverLoading() {
  return (
    <div className="flex-1 w-full px-6 lg:px-8 py-12 min-h-screen bg-slate-50/50">
      <div className="max-w-7xl mx-auto">
        {/* Header Skeleton */}
        <div className="flex flex-col gap-4 mb-12">
          <div className="w-48 h-4 bg-slate-200 rounded-full animate-pulse" />
          <div className="w-1/2 h-12 bg-slate-200 rounded-2xl animate-pulse" />
          <div className="w-2/3 h-6 bg-slate-200 rounded-xl animate-pulse" />
        </div>

        {/* FilterBar Skeleton */}
        <div className="institutional-card bg-white p-8 mb-12 flex flex-col gap-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex flex-col gap-3">
                <div className="w-24 h-3 bg-slate-100 rounded-full animate-pulse" />
                <div className="w-full h-12 bg-slate-50 rounded-xl animate-pulse" />
              </div>
            ))}
          </div>
        </div>

        {/* Results Skeleton */}
        <div className="institutional-card bg-white p-10 min-h-[600px]">
          <div className="flex justify-between items-center mb-10 pb-8 border-b border-slate-50">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-primary/20 rounded-full animate-pulse" />
              <div className="w-64 h-4 bg-slate-100 rounded-full animate-pulse" />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="flex flex-col gap-6 p-6 border border-slate-50 rounded-[32px]">
                <div className="w-full aspect-[4/3] bg-slate-50 rounded-2xl animate-pulse" />
                <div className="flex flex-col gap-3">
                  <div className="w-3/4 h-6 bg-slate-100 rounded-full animate-pulse" />
                  <div className="w-1/2 h-4 bg-slate-50 rounded-full animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
