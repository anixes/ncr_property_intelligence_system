'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Map, { Marker, NavigationControl, Popup } from 'react-map-gl/maplibre';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { motion, AnimatePresence } from 'framer-motion';
import { Compass, BarChart3, ChevronRight, X } from 'lucide-react';
import Link from 'next/link';

export default function SpatialMap() {
  const [viewState, setViewState] = useState({
    longitude: 77.0689,
    latitude: 28.3949,
    zoom: 11.5,
    pitch: 45,
    bearing: -17.6
  });

  const [mode, setMode] = useState<'buy' | 'rent'>('buy');
  const [properties, setProperties] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPin, setSelectedPin] = useState<any | null>(null);

  useEffect(() => {
    // Fetch top properties for the current mode
    const fetchProperties = async () => {
      setLoading(true);
      try {
        const response = await fetch('http://localhost:8000/discover/hotspots?listing_type=' + mode);
        const data = await response.json();
        if (data.status === 'success') {
            // Combine hotspots and featured, avoiding duplicates
            const all = [...data.hotspots, ...data.featured];
            // Remove duplicates by ID or name
            const unique = all.filter((v, i, a) => a.findIndex(t => (t.id === v.id)) === i);
            setProperties(unique);
        }
      } catch (err) {
        console.error('Failed to fetch spatial data', err);
      }
      setLoading(false);
    };
    fetchProperties();
  }, [mode]);

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
          return (
            <Marker 
              key={i} 
              longitude={p.longitude} 
              latitude={p.latitude}
              anchor="bottom"
              onClick={e => {
                e.originalEvent.stopPropagation();
                setSelectedPin(p);
              }}
            >
              <div className="relative group cursor-pointer transition-transform hover:scale-125 z-10 hover:z-50">
                <div className={`w-4 h-4 rounded-full border-2 border-white shadow-[0_0_15px_rgba(255,255,255,0.5)] ${mode === 'buy' ? 'bg-[#bd9dff]' : 'bg-[#10b981]'}`} />
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
                  <h4 className="font-headline font-black text-sm uppercase tracking-wider text-white/80">{selectedPin.sector || selectedPin.city}</h4>
                  <p className="text-xl font-black">{selectedPin.price_str || selectedPin.price}</p>
                </div>
                <button onClick={() => setSelectedPin(null)} className="text-white/40 hover:text-white transition-colors">
                  <X className="w-4 h-4" />
                </button>
              </div>
              
              <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-white/10">
                <div>
                  <span className="block text-[9px] text-white/40 uppercase tracking-widest font-black">Score</span>
                  <span className="block text-sm font-bold text-primary">{selectedPin.institutional_score || selectedPin.score || '--'}</span>
                </div>
                <div>
                  <span className="block text-[9px] text-white/40 uppercase tracking-widest font-black">Yield/ROI</span>
                  <span className="block text-sm font-bold text-[#10b981]">{selectedPin.yield_rate || selectedPin.roi || '--'}</span>
                </div>
              </div>
            </div>
          </Popup>
        )}
      </Map>

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
