import { PropertyListing } from '@/types';
import PropertyCard from '../shared/PropertyCard';
import SkeletonCard from '../shared/SkeletonCard';
import { Layers } from 'lucide-react';

interface ResultsGridProps {
  listings: PropertyListing[];
  isLoading: boolean;
  error: string | null;
}

export default function ResultsGrid({ listings, isLoading, error }: ResultsGridProps) {
  if (error) {
    return (
      <div className="w-full p-8 mt-8 glass-card border-red-500/30 text-center animate-in fade-in duration-500">
        <div className="w-12 h-12 bg-red-500/10 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <Layers className="w-6 h-6" />
        </div>
        <h3 className="text-xl font-bold text-foreground">Discovery Engine Offline</h3>
        <p className="text-red-500/80 mt-2">{error}</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 py-8">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => (
          <SkeletonCard key={`skel-${i}`} />
        ))}
      </div>
    );
  }

  if (listings.length === 0) {
    return (
      <div className="w-full flex flex-col items-center justify-center p-16 mt-8 rounded-2xl border border-dashed border-white/10 bg-white/5 h-[400px] text-center animate-in fade-in duration-500">
        <div className="p-4 bg-white/5 rounded-full mb-4">
          <Layers className="w-8 h-8 text-foreground/50" />
        </div>
        <h3 className="text-lg font-bold text-foreground">No Listings Found</h3>
        <p className="text-sm text-foreground/50 max-w-sm mt-2">
          Try expanding your budget range or modifying your BHK configuration. The database contains 43,000+ records but strict filters may yield zero results.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 py-8">
      {listings.map((listing, idx) => (
        <div 
           key={`listing-${idx}`} 
           className="animate-in fade-in slide-in-from-bottom-8 fill-mode-both"
           style={{ animationDelay: `${idx * 50}ms`, animationDuration: '500ms' }}
        >
          <PropertyCard property={listing} />
        </div>
      ))}
    </div>
  );
}
