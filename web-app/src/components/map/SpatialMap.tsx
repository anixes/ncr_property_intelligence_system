'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Map, { Marker, NavigationControl, Popup } from 'react-map-gl/maplibre';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { motion, AnimatePresence } from 'framer-motion';
import { Compass, BarChart3, ChevronRight, X, Sparkles } from 'lucide-react';
import { formatNCRPrice, formatArea } from '@/utils/format';
import Link from 'next/link';
import { PropertyDeepDive } from '@/components/dashboard/PropertyDeepDive';

export default function SpatialMap() {
  const [hasMounted, setHasMounted] = useState(false);
  const [viewState, setViewState] = useState({
    longitude: 77.10,
    latitude: 28.58,
    zoom: 9.5,
    pitch: 40,
    bearing: 0
  });

  const [mode, setMode] = useState<'buy' | 'rent'>('buy');
  const [properties, setProperties] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPin, setSelectedPin] = useState<any | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

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
        onMove={(evt: any) => setViewState(evt.viewState)}
        mapLib={maplibregl}
        mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
        attributionControl={false}
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
                setSelectedPin(p);
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

        {/* POPUP */}
        {selectedPin && (
          <Popup
            longitude={selectedPin.longitude}
            latitude={selectedPin.latitude}
            anchor="bottom"
            offset={20}
            onClose={() => setSelectedPin(null)}
            closeButton={false}
            closeOnClick={false}
            className="spatial-popup"
          >
            <div className="bg-[#131314] border border-white/10 rounded-xl p-4 shadow-2xl min-w-[240px] text-white font-sans">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h4 className="font-headline font-black text-xs uppercase tracking-widest text-white/40 mb-1">{selectedPin.society || selectedPin.project || 'Institutional Asset'}</h4>
                  <p className="text-xl font-black text-white">{formatNCRPrice(selectedPin.price || selectedPin.total_price)}</p>
                  <p className="text-[10px] font-bold text-white/40 uppercase tracking-tighter">{selectedPin.sector || selectedPin.city}</p>
                </div>
                <button onClick={() => setSelectedPin(null)} className="text-white/40 hover:text-white transition-colors">
                  <X className="w-4 h-4" />
                </button>
              </div>
              
              <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-white/10">
                <div>
                  <span className="block text-[9px] text-white/40 uppercase tracking-widest font-black">Score</span>
                  <span className="block text-sm font-bold text-primary">{(selectedPin.institutional_score || selectedPin.unified_score || 0).toFixed(0)}</span>
                </div>
                <div>
                  <span className="block text-[9px] text-white/40 uppercase tracking-widest font-black">Area/BHK</span>
                  <span className="block text-sm font-bold text-[#10b981]">{selectedPin.bhk || '--'} BHK / {formatArea(selectedPin.area || selectedPin.total_sqft)}</span>
                </div>
              </div>
              
              <div className="flex flex-col gap-2 mt-4">
                <button 
                  onClick={() => setIsDrawerOpen(true)}
                  className="w-full flex items-center justify-center gap-2 py-2.5 bg-primary text-[#0e0e0f] text-[10px] font-black uppercase tracking-widest rounded-lg hover:bg-primary/90 transition-all shadow-lg active:scale-95"
                >
                  Intelligence Report
                  <BarChart3 className="w-3 h-3" />
                </button>
                
                <Link 
                  href={`/dashboard?city=${encodeURIComponent(selectedPin.city || '')}&sector=${encodeURIComponent(selectedPin.sector || selectedPin.locality || '')}&area=${selectedPin.area || selectedPin.total_sqft || ''}&bhk=${selectedPin.bhk || ''}`}
                  className="w-full flex items-center justify-center gap-2 py-2.5 bg-white/5 border border-white/10 text-white text-[10px] font-black uppercase tracking-widest rounded-lg hover:bg-white/10 transition-all active:scale-95"
                >
                  Estimate Value
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </Popup>
        )}
      </Map>

      {/* INTELLIGENCE SIDEBAR (PROPERTY DRAWER) */}
      <PropertyDeepDive 
        item={selectedPin} 
        isOpen={isDrawerOpen} 
        onClose={() => setIsDrawerOpen(false)} 
        intent={mode}
      />

      {/* Tactical HUD Overlay */}
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

        <div className="bg-[#131314]/95 backdrop-blur-md border border-white/20 rounded-xl p-3 shadow-2xl pointer-events-auto">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse shadow-[0_0_8px_rgba(189,157,255,0.6)]" />
            <span className="text-[10px] font-black uppercase tracking-[0.15em] text-white/80">Market Saturation</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white leading-none tracking-tight">
              {properties.length}
            </span>
            <span className="text-[10px] font-black text-white/60 uppercase tracking-widest">
              NCR Active Assets
            </span>
          </div>
        </div>
        <button 
          onClick={() => setViewState({ longitude: 77.10, latitude: 28.58, zoom: 9.5, pitch: 40, bearing: 0 })}
          className="pointer-events-auto px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl text-[10px] font-black uppercase tracking-widest text-white transition-all flex items-center gap-2 w-fit shadow-xl"
        >
          <Compass className="w-3.5 h-3.5" />
          Recenter Region
        </button>
      </div>

      {/* Embedded Map Controls */}
      <div className="absolute top-4 right-4 flex bg-[#1a1a1c]/90 backdrop-blur-md p-1 rounded-full border border-white/10 z-10 shadow-2xl">
        <button 
          onClick={() => setMode('buy')}
          className={`px-3 py-1.5 rounded-full text-[10px] font-black tracking-widest uppercase transition-all duration-300 flex items-center justify-center gap-1 min-w-[70px] ${mode === 'buy' ? 'bg-[#bd9dff] text-[#0e0e0f] shadow-[0_0_10px_rgba(189,157,255,0.3)]' : 'text-white/60 hover:text-white'}`}
        >
          Buy
        </button>
        <button 
          onClick={() => setMode('rent')}
          className={`px-3 py-1.5 rounded-full text-[10px] font-black tracking-widest uppercase transition-all duration-300 flex items-center justify-center gap-1 min-w-[70px] ${mode === 'rent' ? 'bg-[#10b981] text-[#0e0e0f] shadow-[0_0_10px_rgba(16,185,129,0.3)]' : 'text-white/60 hover:text-white'}`}
        >
          Rent
        </button>
      </div>
      
      {/* Global CSS for MapLibre tweaks if needed */}
      <style dangerouslySetInnerHTML={{__html: `
        .spatial-popup .maplibregl-popup-content, .spatial-popup .mapboxgl-popup-content {
            background: transparent !important;
            padding: 0 !important;
            box-shadow: none !important;
        }
        .spatial-popup .maplibregl-popup-tip, .spatial-popup .mapboxgl-popup-tip {
            border-top-color: #131314 !important;
        }
      `}} />
    </div>
  );
}
