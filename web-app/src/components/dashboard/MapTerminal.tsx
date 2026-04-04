'use client';

import React, { useMemo, useState } from 'react';
import DeckGL from '@deck.gl/react';
import { H3HexagonLayer } from '@deck.gl/geo-layers';
import { ColumnLayer } from '@deck.gl/layers';
import { Map } from 'react-map-gl/mapbox';
import { Activity, Crosshair, Globe, Maximize2 } from 'lucide-react';
import 'mapbox-gl/dist/mapbox-gl.css';

const INITIAL_VIEW_STATE = {
  longitude: 77.0266,
  latitude: 28.4595,
  zoom: 12,
  pitch: 45,
  bearing: 0
};

const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';

interface MapProps {
  hotspots?: any[];
  listings?: any[];
}

export default function MapTerminal({ hotspots = [], listings = [] }: MapProps) {
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);

  const layers = useMemo(() => [
    new H3HexagonLayer({
      id: 'h3-layer',
      data: hotspots,
      pickable: true,
      wireframe: false,
      filled: true,
      extruded: true,
      elevationScale: 50,
      getHexagon: (d: any) => d.h3_id,
      getFillColor: (d: any) => [255, (1 - d.median_price_sqft / 15000) * 255, 0, 180],
      getElevation: (d: any) => Math.log1p(d.density) * 10
    }),
    new ColumnLayer({
      id: 'column-layer',
      data: listings,
      diskResolution: 12,
      radius: 100,
      extruded: true,
      pickable: true,
      elevationScale: 10,
      getPosition: (d: any) => [d.longitude, d.latitude],
      getFillColor: [0, 163, 255, 200],
      getElevation: (d: any) => (d.unified_score * 40) + 80
    })
  ], [hotspots, listings]);

  return (
    <div className="w-full h-full relative overflow-hidden rounded-[40px] border border-white/10 group shadow-3xl bg-[#0e0e0f]">
      
      {/* 📡 WORKSTATION HUD OVERLAYS */}
      
      {/* Top HUD: Status Bar */}
      <div className="absolute top-6 left-6 right-6 z-30 flex justify-between items-center pointer-events-none">
        <div className="flex items-center gap-4">
          <div className="glass-panel-luxe px-5 py-2 rounded-full flex items-center gap-3 border border-primary/20 pointer-events-auto">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse shadow-[0_0_10px_#bd9dff]" />
            <span className="text-[10px] font-black text-white tracking-[0.2em] uppercase">Tactical Scan Active</span>
          </div>
          <div className="hidden sm:flex glass-panel-luxe px-4 py-2 rounded-full items-center gap-3 pointer-events-auto">
             <Activity className="w-3 h-3 text-white/40" />
             <span className="text-[9px] font-bold text-white/40 uppercase tracking-widest">FPS: 60.0 • LAT: 低</span>
          </div>
        </div>
        <div className="flex items-center gap-3 sm:gap-4 pointer-events-auto">
           <button className="h-10 w-10 glass-panel-luxe rounded-full flex items-center justify-center text-white/60 hover:text-primary transition-colors">
              <Maximize2 className="w-4 h-4" />
           </button>
        </div>
      </div>

      {/* Bottom HUD: Coordinates & Tracking */}
      <div className="absolute bottom-6 left-6 right-6 z-30 flex flex-col sm:flex-row justify-between items-end gap-4 pointer-events-none">
        <div className="glass-panel-luxe p-6 rounded-[2rem] flex flex-col gap-4 border border-white/10 pointer-events-auto min-w-[200px]">
           <div className="flex items-center gap-3">
              <Crosshair className="w-4 h-4 text-primary" />
              <span className="text-[10px] font-black text-white tracking-[0.3em] uppercase">Target Vectoring</span>
           </div>
           <div className="grid grid-cols-2 gap-8 h-12 items-center">
              <div className="flex flex-col">
                 <span className="text-[8px] opacity-30 font-black tracking-widest">LATITUDE</span>
                 <span className="text-[11px] font-black font-mono text-white tracking-widest">{viewState.latitude.toFixed(4)}</span>
              </div>
              <div className="flex flex-col border-l border-white/10 pl-6">
                 <span className="text-[8px] opacity-30 font-black tracking-widest">LONGITUDE</span>
                 <span className="text-[11px] font-black font-mono text-white tracking-widest">{viewState.longitude.toFixed(4)}</span>
              </div>
           </div>
        </div>

        <div className="hidden lg:flex items-center gap-4">
           <div className="glass-panel-luxe px-6 py-4 rounded-3xl border border-white/10 pointer-events-auto group/intel">
              <div className="flex items-center gap-3">
                 <Globe className="w-4 h-4 text-primary group-hover/intel:scale-110 transition-transform" />
                 <span className="text-[10px] font-black text-white tracking-[0.4em] uppercase">Alpha Horizon</span>
              </div>
           </div>
        </div>
      </div>

      {/* MAP ENGINE */}
      <div className="absolute inset-0 z-10 grayscale opacity-90 contrast-125 brightness-75 group-hover:brightness-100 transition-all duration-[2000ms]">
        <DeckGL
          initialViewState={viewState}
          onViewStateChange={({ viewState }: any) => setViewState(viewState)}
          controller={true}
          layers={layers}
          getTooltip={({ object }: any) => object && (object.h3_id || object.society)}
        >
          <Map mapStyle={MAP_STYLE} />
        </DeckGL>
      </div>

    </div>
  );
}

