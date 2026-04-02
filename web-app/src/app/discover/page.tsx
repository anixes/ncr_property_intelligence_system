import { Suspense } from 'react';
import { Metadata } from 'next';
import DiscoverContent from '@/components/discover/DiscoverContent';
import DiscoverLoading from './loading';

export const metadata: Metadata = {
  title: 'Property Discovery — NCR Realty',
  description: 'Advanced property search for Gurgaon, Noida, and NCR. Filter by yield, value delta, and decision score. Scanning 43,000+ verified units.',
};

export default function DiscoverPage() {
  return (
    <Suspense fallback={<DiscoverLoading />}>
      <DiscoverContent />
    </Suspense>
  );
}
