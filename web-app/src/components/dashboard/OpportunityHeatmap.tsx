'use client';

import React, { useState, useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { Hotspot } from '@/types';
import api from '@/lib/api';
import type { Map as MapType } from 'leaflet';

// Use dynamic imports for Leaflet as it requires a window object.
const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false }
);
const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
);
const Polygon = dynamic(
  () => import('react-leaflet').then((mod) => mod.Polygon),
  { ssr: false }
);
const Tooltip = dynamic(
  () => import('react-leaflet').then((mod) => mod.Tooltip),
  { ssr: false }
);

const OpportunityHeatmap = ({ city }: { city?: string }) => {
  const [activeListingType, setActiveListingType] = useState<'buy' | 'rent'>('buy');
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // H3 Engine dynamic import per turn-based requirement
  const [cellGeometries, setCellGeometries] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        // Correcting signature: city first, returns direct array
        const data = await api.getHotspots(city, activeListingType);
        setHotspots(data);
        
        // Compute geometries using H3-JS
        const h3 = await import('h3-js');
        const geometries = data.map((spot: Hotspot, index: number) => {
          const boundary = h3.cellToBoundary(spot.h3_res8);
          // Normalized value for OKLCH color generation (0-1)
          const allPrices = data.map(d => d.median_price_sqft);
          const maxPrice = allPrices.length > 0 ? Math.max(...allPrices) : 1;
          const weight = spot.median_price_sqft / maxPrice;
          
          return {
            // Composite key to prevent React duplicate key warnings
            key: `${spot.h3_res8}-${index}-${activeListingType}`,
            id: spot.h3_res8,
            positions: boundary,
            weight,
            spot
          };
        });
        setCellGeometries(geometries);
      } catch (err) {
        console.error('Heatmap load failed', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [activeListingType, city]);

  // Color generator using institutional OKLCH logic
  const getCellColor = (weight: number) => {
    // Dynamic weight mapping to institutional brand colors
    // Low: Neutral-ish / Mid: Sky / High: Brand (OKLCH)
    const l = 0.5 + (weight * 0.3); // 50% to 80% lightness
    const c = 0.15; // Moderate chroma
    const h = 180 + (weight * 120); // Cyan to Lime/Yellow
    return `oklch(${l} ${c} ${h})`;
  };

  return (
    <div className="w-full h-full relative">
      <div className="absolute top-20 right-6 z-[1000] flex flex-col gap-2">
        <button 
          onClick={() => setActiveListingType('buy')}
          className={`px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest border transition-all ${
            activeListingType === 'buy' 
              ? 'bg-brand text-black border-brand shadow-[0_0_15px_rgba(var(--brand-rgb),0.3)]' 
              : 'bg-black/60 text-white/40 border-white/10 hover:border-white/20'
          }`}
        >
          Institutional Buy
        </button>
        <button 
          onClick={() => setActiveListingType('rent')}
          className={`px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest border transition-all ${
            activeListingType === 'rent' 
              ? 'bg-brand text-black border-brand shadow-[0_0_15px_rgba(var(--brand-rgb),0.3)]' 
              : 'bg-black/60 text-white/40 border-white/10 hover:border-white/20'
          }`}
        >
          Yield Max Rent
        </button>
      </div>

      <MapContainer 
        center={[28.5355, 77.3910]} 
        zoom={11} 
        scrollWheelZoom={false}
        className="w-full h-full grayscale-[0.8] contrast-[1.2]"
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        {cellGeometries.map((cell) => (
          <Polygon
            key={cell.key}
            positions={cell.positions}
            pathOptions={{
              fillColor: getCellColor(cell.weight),
              fillOpacity: 0.3 + (cell.weight * 0.4),
              color: 'rgba(255,255,255,0.05)',
              weight: 1
            }}
          >
            <Tooltip sticky className="bg-black/80 border-white/10 text-white/90 rounded-lg backdrop-blur-xl p-3 shadow-2xl">
              <div className="font-mono space-y-2">
                <p className="text-[9px] uppercase tracking-widest text-[#CBFF00]">Intelligence Cell: {cell.id}</p>
                <div className="h-px bg-white/10" />
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-[8px] text-white/40">MEDIAN VALUE</p>
                    <p className="text-sm font-bold">₹{cell.spot.median_price_sqft.toLocaleString()}/sqft</p>
                  </div>
                  <div>
                    <p className="text-[8px] text-white/40">DENSITY</p>
                    <p className="text-sm font-bold">{cell.spot.density} Listings</p>
                  </div>
                </div>
              </div>
            </Tooltip>
          </Polygon>
        ))}
      </MapContainer>

      {isLoading && (
        <div className="absolute inset-0 bg-black/40 backdrop-blur-sm z-[2000] flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 border-4 border-brand/20 border-t-brand rounded-full animate-spin" />
            <p className="text-[10px] font-mono tracking-[0.3em] text-brand/80 animate-pulse">RECALIBRATING SPATIAL GRID...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default OpportunityHeatmap;
