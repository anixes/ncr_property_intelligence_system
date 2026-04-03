'use client';

import React, { useMemo } from 'react';
import DeckGL from '@deck.gl/react';
import { H3HexagonLayer } from '@deck.gl/geo-layers';
import { ColumnLayer } from '@deck.gl/layers';
import { Map } from 'react-map-gl/mapbox';
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
    <div className="w-full h-full relative overflow-hidden rounded-3xl border border-white/5">
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={layers}
      >
        <Map mapStyle={MAP_STYLE} />
      </DeckGL>
    </div>
  );
}
