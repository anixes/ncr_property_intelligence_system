'use client';

import React, { useState, useEffect, useMemo, useRef } from 'react';
import Map, { Marker, NavigationControl, Popup } from 'react-map-gl/maplibre';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, Building, Ruler, Info, Target, Layers, Navigation, Compass, BarChart3, ChevronRight, X, Sparkles } from 'lucide-react';
import { PropertyAsset, Recommendation } from '@/types';
import { formatNCRPrice, formatArea } from '@/utils/format';
import Link from 'next/link';
import { PropertyDeepDive } from '../dashboard/PropertyDeepDive';

export default function SpatialMap() {
  const [hasMounted, setHasMounted] = useState(false);
  const [viewState, setViewState] = useState({
    longitude: 77.10,
    latitude: 28.58,
    zoom: typeof window !== 'undefined' && window.innerWidth < 768 ? 8.2 : 9.5,
    pitch: 40,
    bearing: 0
  });

  const [mode, setMode] = useState<'buy' | 'rent'>('buy');
  const [properties, setProperties] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPin, setSelectedPin] = useState<any | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const mapRef = useRef<any>(null);

  const handleMarkerClick = (property: any) => {
    setSelectedPin(property);
    setIsDrawerOpen(true);

    // Dynamic Camera Offset: Shift map to the left to clear the right sidebar
    if (mapRef.current) {
      const lat = property.latitude || property.lat;
      const lon = property.longitude || property.lon;
      
      if (lat && lon) {
        mapRef.current.easeTo({
          center: [lon, lat],
          // Offset the center so marker is on the left 1/3rd (desktop) or center (mobile)
          offset: window.innerWidth > 1024 ? [150, 0] : [0, 0], 
          duration: 1000,
          zoom: Math.max(viewState.zoom, 12),
          padding: { right: window.innerWidth > 1024 ? 400 : 0 }
        });
      }
    }
  };

  useEffect(() => {
    setHasMounted(true);
  }, []);
  
  // Identify the "top" hotspot for the HUD overlay
  const topInsight = useMemo(() => {
    if (!properties.length) return null;
    return properties.reduce((prev, current) => 
      ((prev.institutional_score || prev.unified_score || 0) > (current.institutional_score || current.unified_score || 0)) ? prev : current
    );
  }, [properties]);

  useEffect(() => {
    // Fetch top properties for the current mode
    const fetchProperties = async () => {
      setLoading(true);
      try {
        const response = await fetch('/api/discovery?listing_type=' + mode);
        const data = await response.json();
        if (data.status === 'success') {
            // Combine hotspots and featured, avoiding duplicates
            const all = [...(data.hotspots || []), ...(data.featured || [])];
            
            // Custom high-fidelity deduplication (since many lack distinct IDs)
            const unique = [];
            const seen = new Set();
            
            for (const p of all) {
              const key = `${p.society || p.sector || ''}-${p.locality || ''}-${p.price || ''}-${p.h3_index || ''}`;
              if (!seen.has(key)) {
                seen.add(key);
                
                // ADD SUBTLE JITTER to overlapping properties
                // This makes and sector with multiple listings look "alive"
                const jitterLat = (Math.random() - 0.5) * 0.002;
                const jitterLon = (Math.random() - 0.5) * 0.002;
                
                unique.push({
                  ...p,
                  latitude: (p.latitude || 0) + jitterLat,
                  longitude: (p.longitude || 0) + jitterLon
                });
              }
            }
            setProperties(unique);
        }
      } catch (err) {
        console.error('Failed to fetch spatial data', err);
      }
      setLoading(false);
    };
    fetchProperties();
  }, [mode]);

  if (!hasMounted) {
    return (
      <div className="w-full h-full bg-[#0e0e0f] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
          <span className="text-[10px] font-black uppercase tracking-widest text-white/20">Syncing NCR Spatial Grid...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full bg-[#0e0e0f] overflow-hidden">
      {/* MAP LAYER */}
      <Map
        {...viewState}
        ref={mapRef}
        onMove={(evt: any) => setViewState(evt.viewState)}
        mapLib={maplibregl}
        mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
        attributionControl={false}
        onClick={() => {
          if (isDrawerOpen) setIsDrawerOpen(false);
        }}
      >
        <NavigationControl position="bottom-right" showCompass={false} />

        {/* MARKERS */}
        {properties.map((p, i) => {
          if (!p.latitude || !p.longitude) return null;
          const score = p.institutional_score || p.unified_score || 0;
          const isHighAlpha = score > 90;
          
          return (
            <Marker 
              key={`${i}-${p.h3_index}`}
              longitude={p.longitude} 
              latitude={p.latitude}
              anchor="bottom"
              onClick={e => {
                e.originalEvent.stopPropagation();
                handleMarkerClick(p);
              }}
            >
              <div className="relative group cursor-pointer transition-transform hover:scale-125 z-10 hover:z-50">
                {/* Visual Pulse for High Alpha Assets */}
                {isHighAlpha && (
                  <motion.div 
                    animate={{ scale: [1, 2], opacity: [0.3, 0] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                    className="absolute inset-0 bg-yellow-400 rounded-full blur-md"
                  />
                )}
                <div 
                  className={`w-3 h-3 rounded-full border border-white shadow-xl transition-all duration-300
                    ${isHighAlpha ? 'bg-yellow-400 border-yellow-200' : (mode === 'buy' ? 'bg-[#bd9dff]' : 'bg-[#10b981]')}`} 
                />
              </div>
            </Marker>
          );
        })}
      </Map>

      {/* INTELLIGENCE SIDEBAR (PROPERTY DRAWER) */}
      <PropertyDeepDive 
        item={selectedPin} 
        isOpen={isDrawerOpen} 
        onClose={() => setIsDrawerOpen(false)} 
        intent={mode}
      />

      {/* Tactical HUD Overlay *) */}
      <div className="absolute bottom-4 left-4 pointer-events-none z-10 flex flex-col gap-3">
        {/* Dynamic Insight Card - Only shows if we have high-alpha properties */}
        {topInsight && (topInsight.institutional_score || topInsight.unified_score || 0) > 85 && (
          <AnimatePresence>
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-primary/10 backdrop-blur-xl border border-primary/30 rounded-xl p-3 shadow-2xl shadow-primary/10 max-w-[200px]"
            >
              <div className="flex items-center gap-2 mb-1">
                <Sparkles className="w-3 h-3 text-primary animate-pulse" />
                <span className="text-[9px] font-black uppercase tracking-widest text-primary">Live Deep-Value Signal</span>
              </div>
              <p className="text-[11px] font-black text-white leading-tight uppercase mb-1">
                {topInsight.society || topInsight.sector || topInsight.city}
              </p>
              <div className="flex items-center gap-2">
                <span className="text-white/60 text-[8px] font-bold uppercase">Alpha:</span>
                <span className="text-xs font-black text-primary">{(topInsight.institutional_score || topInsight.unified_score || 0).toFixed(1)}</span>
              </div>
            </motion.div>
          </AnimatePresence>
        )}

        <div className="bg-[#131314]/80 backdrop-blur-xl border border-white/10 rounded-xl p-2.5 sm:p-3 shadow-2xl pointer-events-auto transition-all duration-500">
          <div className="flex items-center gap-2.5 mb-1.5">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse shadow-[0_0_8px_rgba(189,157,255,0.6)]" />
            <span className="text-[8px] sm:text-[10px] font-black uppercase tracking-[0.15em] text-white/80">Market Saturation</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-black text-white leading-none tracking-tight">
              {properties.length}
            </span>
            <span className="text-[8px] sm:text-[10px] font-black text-white/50 uppercase tracking-widest leading-none">
              NCR Assets
            </span>
          </div>
        </div>
        <button 
          onClick={() => setViewState({ longitude: 77.10, latitude: 28.58, zoom: 9.5, pitch: 40, bearing: 0 })}
          className="pointer-events-auto px-4 py-2.5 bg-white/5 backdrop-blur-xl hover:bg-white/10 border border-white/10 rounded-xl text-[9px] font-black uppercase tracking-widest text-white transition-all flex items-center gap-2 w-fit shadow-2xl active:scale-95"
        >
          <Compass className="w-3 h-3 text-primary" />
          Recenter
        </button>
      </div>

      {/* Embedded Map Controls */}
      <div className="absolute top-4 sm:top-6 right-4 flex bg-[#1a1a1c]/80 backdrop-blur-xl p-1 rounded-full border border-white/10 z-10 shadow-3xl transition-all duration-500">
        <button 
          onClick={() => setMode('buy')}
          className={`px-4 py-2 sm:px-6 sm:py-2.5 rounded-full text-[9px] sm:text-[10px] font-black tracking-widest uppercase transition-all duration-500 flex items-center justify-center gap-1 min-w-[80px] sm:min-w-[90px] ${mode === 'buy' ? 'bg-[#bd9dff] text-[#0e0e0f] shadow-[0_0_20px_rgba(189,157,255,0.2)]' : 'text-white/40 hover:text-white'}`}
        >
          Buy
        </button>
        <button 
          onClick={() => setMode('rent')}
          className={`px-4 py-2 sm:px-6 sm:py-2.5 rounded-full text-[9px] sm:text-[10px] font-black tracking-widest uppercase transition-all duration-500 flex items-center justify-center gap-1 min-w-[80px] sm:min-w-[90px] ${mode === 'rent' ? 'bg-[#10b981] text-[#0e0e0f] shadow-[0_0_20px_rgba(16,185,129,0.2)]' : 'text-white/40 hover:text-white'}`}
        >
          Rent
        </button>
      </div>
    </div>
  );
}
