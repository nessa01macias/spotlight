'use client';

import { useEffect, useRef } from 'react';
import Map, { Layer, Source } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

interface HeatMapProps {
  center?: [number, number];
  zoom?: number;
  data?: any; // GeoJSON data for heatmap
  onAreaClick?: (areaId: string) => void;
  className?: string;
}

/**
 * HeatMap - Mapbox with desaturated base, 2-color ramp, no legend
 *
 * Features:
 * - Clean, minimal markers
 * - Soft gradient overlay (green = high opportunity)
 * - Tooltips on hover (not legends)
 * - No UI clutter
 */
export default function HeatMap({
  center = [24.9384, 60.1695], // Helsinki center
  zoom = 11,
  data,
  onAreaClick,
  className = '',
}: HeatMapProps) {
  const mapRef = useRef<any>(null);

  // Desaturated basemap style
  const mapStyle = 'mapbox://styles/mapbox/light-v11'; // Light, minimal style

  // Heatmap layer config (2-color ramp: light green → accent green)
  const heatmapLayer: any = {
    id: 'heatmap',
    type: 'heatmap' as const,
    paint: {
      // Color ramp: transparent → light green → accent green
      'heatmap-color': [
        'interpolate',
        ['linear'],
        ['heatmap-density'],
        0, 'rgba(0, 0, 0, 0)',
        0.2, '#F2F7FF',
        0.4, '#C9DCFF',
        0.6, '#B2C9FF',
        0.8, '#10B981',
        1, '#059669'
      ] as any,
      'heatmap-radius': 30,
      'heatmap-opacity': 0.7,
    },
  };

  return (
    <div className={`relative ${className}`}>
      <Map
        ref={mapRef}
        mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN || 'your-mapbox-token'}
        initialViewState={{
          longitude: center[0],
          latitude: center[1],
          zoom: zoom,
        }}
        style={{ width: '100%', height: '100%' }}
        mapStyle={mapStyle}
        minZoom={9}
        maxZoom={15}
      >
        {data && (
          <Source id="opportunities" type="geojson" data={data}>
            <Layer {...heatmapLayer} />
          </Source>
        )}
      </Map>

      {/* Loading state / placeholder if no token */}
      {!process.env.NEXT_PUBLIC_MAPBOX_TOKEN && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-50 border border-gradient-100 rounded-lg">
          <div className="text-center p-8">
            <p className="text-neutral-600">Map preview</p>
            <p className="text-sm text-neutral-500 mt-2">
              Set NEXT_PUBLIC_MAPBOX_TOKEN to enable
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
