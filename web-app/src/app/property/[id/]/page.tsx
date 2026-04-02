import { Suspense } from 'react';
import { Metadata } from 'next';
import PropertyDetailClient from '@/components/property/PropertyDetailClient';

interface Props {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export async function generateMetadata(
  { searchParams }: Props
): Promise<Metadata> {
  const s = await searchParams;
  const society = (s.s as string) || 'Premium Asset';
  const locality = (s.l as string) || 'NCR Sector';
  const deltaStr = (s.v as string) || '0';
  const delta = Number(deltaStr);
  const price = Number(s.p) || 0;

  const alphaTag = delta <= 0 ? `${Math.abs(delta * 100).toFixed(0)}% Underpriced` : 'Market Validated';
  
  return {
    title: `${society} — ${alphaTag} Analysis | NCR Intelligence`,
    description: `Institutional property report for ${society}, ${locality}. Asset value: ₹${(price / 10000000).toFixed(2)} Cr. Yield Analysis and Market Narrative included.`,
  };
}

export default async function PropertyDetailPage({ params, searchParams }: Props) {
  const s = await searchParams;
  
  // Reconstruct property object for the client shell
  const propertyData = {
    society: s.s || 'Premium Asset',
    locality: s.l || 'NCR Sector',
    city: s.c || 'NCR',
    price: Number(s.p) || 18000000,
    area: Number(s.a) || 1800,
    bhk: Number(s.b) || 3,
    yield_pct: Number(s.y) || 0.032,
    valuation_pct: Number(s.v) || -0.05,
    unified_score: 8.4,
    listing_type: 'buy',
    price_per_sqft: (Number(s.p) || 18000000) / (Number(s.a) || 1800)
  };

  return (
    <Suspense fallback={
      <div className="flex-1 w-full min-h-screen bg-slate-50/50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin" />
          <span className="label-eyebrow text-slate-400">Archiving Market Intelligence...</span>
        </div>
      </div>
    }>
      <PropertyDetailClient propertyData={propertyData} />
    </Suspense>
  );
}
