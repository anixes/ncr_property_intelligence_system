export default function SkeletonCard() {
  return (
    <div className="glass-card p-6 animate-pulse flex flex-col gap-4">
      <div className="flex justify-between items-start">
        <div className="space-y-3 w-2/3">
          <div className="h-4 bg-white/10 rounded-md w-3/4"></div>
          <div className="h-3 bg-white/5 rounded-md w-1/2"></div>
        </div>
        <div className="h-8 bg-white/10 rounded-full w-20"></div>
      </div>
      
      <div className="h-20 bg-white/5 rounded-xl my-2"></div>
      
      <div className="grid grid-cols-3 gap-2 mt-auto">
        <div className="h-10 bg-white/5 rounded-lg"></div>
        <div className="h-10 bg-white/5 rounded-lg"></div>
        <div className="h-10 bg-white/5 rounded-lg"></div>
      </div>
    </div>
  );
}
