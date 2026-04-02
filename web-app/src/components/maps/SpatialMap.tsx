'use client';

import React, { useMemo, useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Hotspot, PropertyListing } from '@/types';
import { CITY_CENTERS } from '@/lib/constants';

// Dynamically import Leaflet components to avoid SSR issues
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false });
const Polygon = dynamic(() => import('react-leaflet').then(mod => mod.Polygon), { ssr: false });
const CircleMarker = dynamic(() => import('react-leaflet').then(mod => mod.CircleMarker), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false });
const Tooltip = dynamic(() => import('react-leaflet').then(mod => mod.Tooltip), { ssr: false });
const ZoomControl = dynamic(() => import('react-leaflet').then(mod => mod.ZoomControl), { ssr: false });

import * as h3 from 'h3-js';

// Helper to provide reactive map control
const ChangeView = ({ center }: { center: [number, number] }) => {
  // @ts-ignore
  const map = require('react-leaflet').useMap();
  useEffect(() => {
    map.setView(center, map.getZoom());
  }, [center, map]);
  return null;
};

interface SpatialMapProps {
  hotspots?: Hotspot[];
  listings?: PropertyListing[];
  city?: string;
}

export default function SpatialMap({ hotspots = [], listings = [], city = 'Entire NCR' }: SpatialMapProps) {
  const [isMounted, setIsMounted] = useState(false);

  const center = CITY_CENTERS[city] || CITY_CENTERS['Entire NCR'] || { lon: 77.1025, lat: 28.7041 };

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const [isInteracting, setIsInteracting] = useState(false);

  if (!isMounted) {
    return <div className="w-full h-[500px] bg-slate-100 animate-pulse rounded-[32px] border border-slate-200" />;
  }

  return (
    <div 
      className="relative w-full h-[600px] rounded-[32px] overflow-hidden shadow-2xl border border-slate-200 bg-slate-50 group"
      onMouseLeave={() => setIsInteracting(false)}
    >
      <MapContainer
        center={[center.lat, center.lon]}
        zoom={11}
        scrollWheelZoom={false}
        zoomControl={false}
        dragging={!isMounted || (typeof window !== 'undefined' && window.innerWidth < 768 ? isInteracting : true)}
        className="w-full h-full z-0"
      >
        <ChangeView center={[center.lat, center.lon]} />
        <TileLayer
          attribution='&copy; CARTO'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />

        <ZoomControl position="bottomright" />

        {/* 1. Logic Layer: Market Activity (H3 Polygons) */}
        {hotspots.map((h, i) => {
          try {
            const boundary = h3.cellToBoundary(h.h3_res8);
            const positions: [number, number][] = boundary.map((p: number[]) => [p[0], p[1]]);
            
            // Institutional Signal Colors
            const color = h.density > 50 ? 'rgb(239, 68, 68)' : h.density > 20 ? 'rgb(251, 191, 36)' : 'var(--primary)';

            return (
              <Polygon
                key={`h3-${i}`}
                positions={positions}
                pathOptions={{
                  fillColor: color,
                  fillOpacity: 0.1,
                  color: color,
                  weight: 0.5,
                }}
              >
                <Tooltip sticky>
                  <div className="p-3 bg-white text-slate-900 rounded-2xl shadow-2xl border border-slate-100">
                    <span className="label-eyebrow text-slate-400 block mb-1">Concentration Index</span>
                    <span className="text-sm font-black uppercase tracking-tighter">{h.density}% Market Density</span>
                  </div>
                </Tooltip>
              </Polygon>
            );
          } catch (e) {
            return null;
          }
        })}

        {/* 2. Listing Layer: Property Points */}
        {listings.map((l, i) => {
          if (!l.latitude || !l.longitude) return null;
          return (
            <CircleMarker
              key={`list-${i}`}
              center={[l.latitude, l.longitude]}
              radius={8}
              pathOptions={{
                fillColor: 'var(--primary)',
                fillOpacity: 1,
                color: '#fff',
                weight: 2.5,
              }}
            >
              <Popup className="institutional-popup">
                <div className="p-4 min-w-[240px] font-sans">
                  <div className="label-eyebrow text-slate-400 mb-2">Verified Asset</div>
                  <h3 className="text-base font-black text-slate-900 m-0 leading-tight mb-4 uppercase tracking-tighter">{l.society}</h3>
                  <div className="flex justify-between items-center pt-4 border-t border-slate-50">
                    <span className="text-base font-black text-primary tracking-tighter">
                      ₹{l.listing_type === 'buy' ? (l.price / 10000000).toFixed(2) + ' Cr' : (l.price / 1000).toFixed(1) + ' K'}
                    </span>
                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{l.bhk} BHK Suite</span>
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {/* Interaction Shield for Mobile */}
      {!isInteracting && (
        <div 
          className="absolute inset-0 z-[1001] bg-slate-900/5 backdrop-blur-[1px] flex items-center justify-center lg:hidden transition-opacity duration-300"
          onClick={() => setIsInteracting(true)}
        >
          <div className="px-6 py-3 bg-white/90 backdrop-blur-xl rounded-2xl border border-white shadow-2xl shadow-slate-900/10">
             <span className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-900">Tap to Explore Spatial Data</span>
          </div>
        </div>
      )}

      {/* Legend Overlay: Institutional Minimalist */}
      <div className="absolute top-8 left-8 p-6 bg-white/90 backdrop-blur-xl border border-slate-200 rounded-[28px] text-[10px] space-y-3 z-[1000] pointer-events-none shadow-2xl">
        <h4 className="label-eyebrow text-slate-400 mb-4 border-b border-slate-100 pb-3">Spatial Index</h4>
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-red-500/20 rounded-sm border border-red-400" /> 
          <span className="text-slate-900 font-black uppercase tracking-widest">Growth Vector</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 border-2 border-primary/20 rounded-sm bg-primary/10" /> 
          <span className="text-slate-900 font-black uppercase tracking-widest">Market Core</span>
        </div>
        <div className="flex items-center gap-3 pt-2">
           <div className="w-4 h-4 bg-primary rounded-full border-2 border-white shadow-lg" /> 
           <span className="text-slate-900 font-black uppercase tracking-[0.15em]">Verified Asset</span>
        </div>
      </div>
    </div>
  );
}
