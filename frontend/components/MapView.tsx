'use client';

import { useEffect, useRef, useState } from 'react';

interface MapLocation {
  rank: number;
  lat: number;
  lng: number;
  address: string;
  decision: 'MAKE_OFFER' | 'NEGOTIATE' | 'PASS';
}

interface MapViewProps {
  locations: MapLocation[];
  selectedRank?: number;
  onPinClick?: (rank: number) => void;
  apiKey: string;
}

export function MapView({ locations, selectedRank, onPinClick, apiKey }: MapViewProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<any>(null);
  const [markers, setMarkers] = useState<any[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);
  const [useOsm, setUseOsm] = useState(false);

  // Initialize Google Maps API
  useEffect(() => {
    // If no API key, use OSM immediately
    if (!apiKey) {
      setUseOsm(true);
      return;
    }

    // Check if already loaded
    if (window.google?.maps?.Map) {
      setIsLoaded(true);
      return;
    }

    // Check if script is already being loaded
    const existingScript = document.querySelector(`script[src*="maps.googleapis.com"]`);
    if (existingScript) {
      // Wait for existing script to load
      const checkLoaded = setInterval(() => {
        if (window.google?.maps?.Map) {
          setIsLoaded(true);
          clearInterval(checkLoaded);
          setUseOsm(false);
        }
      }, 100);
      return () => clearInterval(checkLoaded);
    }

    // Use a persistent global callback
    const callbackName = 'initGoogleMaps';
    if (!(window as any)[callbackName]) {
      (window as any)[callbackName] = () => {
        // Signal that maps is loaded for all components
        (window as any).googleMapsLoaded = true;
      };
    }

    // Check if already being loaded
    const checkLoaded = setInterval(() => {
      if (window.google?.maps?.Map || (window as any).googleMapsLoaded) {
        setIsLoaded(true);
        clearInterval(checkLoaded);
        setUseOsm(false);
      }
    }, 100);

    // Fallback timer: if Google hasn't initialized soon, switch to OSM
    const fallbackTimer = setTimeout(() => {
      if (!window.google?.maps?.Map) {
        setUseOsm(true);
      }
    }, 2000);

    // Load Google Maps script with callback
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=${callbackName}`;
    script.async = true;
    script.defer = true;
    script.onerror = () => {
      console.error('Failed to load Google Maps script');
      clearInterval(checkLoaded);
      setUseOsm(true);
    };
    document.head.appendChild(script);

    return () => {
      clearInterval(checkLoaded);
      clearTimeout(fallbackTimer);
    };
  }, [apiKey]);

  // Initialize map once API is loaded
  useEffect(() => {
    if (!mapRef.current || !isLoaded || !window.google?.maps?.Map) return;

    // Calculate center from all locations
    const avgLat = locations.reduce((sum, loc) => sum + loc.lat, 0) / locations.length;
    const avgLng = locations.reduce((sum, loc) => sum + loc.lng, 0) / locations.length;

    const newMap = new google.maps.Map(mapRef.current, {
      center: { lat: avgLat, lng: avgLng },
      zoom: 13,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
    });

    setMap(newMap);
  }, [isLoaded, locations]);

  // Add markers when map is ready
  useEffect(() => {
    if (!map || useOsm) return;

    // Clear existing markers
    markers.forEach(marker => marker.setMap && marker.setMap(null));

    // Create new markers
    const newMarkers = locations.map(location => {
      const color = getMarkerColor(location.decision);

      const marker = new google.maps.Marker({
        position: { lat: location.lat, lng: location.lng },
        map,
        label: {
          text: location.rank.toString(),
          color: 'white',
          fontSize: '14px',
          fontWeight: 'bold',
        },
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: selectedRank === location.rank ? 20 : 16,
          fillColor: color,
          fillOpacity: selectedRank === location.rank ? 1 : 0.8,
          strokeColor: 'white',
          strokeWeight: 2,
        },
        title: location.address,
      });

      marker.addListener('click', () => {
        if (onPinClick) {
          onPinClick(location.rank);
        }
      });

      return marker;
    });

    setMarkers(newMarkers);

    // Fit bounds to show all markers
    const bounds = new google.maps.LatLngBounds();
    locations.forEach(loc => bounds.extend({ lat: loc.lat, lng: loc.lng }));
    map.fitBounds(bounds);

    // Add padding
    google.maps.event.addListenerOnce(map, 'bounds_changed', () => {
      const currentZoom = map.getZoom();
      if (currentZoom && currentZoom > 15) {
        map.setZoom(15);
      }
    });
  }, [map, locations, selectedRank, onPinClick, useOsm]);

  // Pan to selected location
  useEffect(() => {
    if (!map || selectedRank === undefined) return;

    const selected = locations.find(loc => loc.rank === selectedRank);
    if (selected && !useOsm) {
      map.panTo({ lat: selected.lat, lng: selected.lng });
      map.setZoom(16);
    }
  }, [map, selectedRank, locations, useOsm]);

  // OSM fallback: load Leaflet from CDN and render
  useEffect(() => {
    if (!useOsm || !mapRef.current) return;

    const ensureLeaflet = async () => {
      // Load CSS
      if (!document.querySelector('link[data-leaflet]')) {
        const link = document.createElement('link');
        link.setAttribute('data-leaflet', 'true');
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        document.head.appendChild(link);
      }
      // Load JS
      if (!(window as any).L) {
        await new Promise<void>((resolve, reject) => {
          const s = document.createElement('script');
          s.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
          s.async = true;
          s.onload = () => resolve();
          s.onerror = () => reject(new Error('Failed to load Leaflet'));
          document.body.appendChild(s);
        });
      }
    };

    const initOsm = async () => {
      await ensureLeaflet();
      const L = (window as any).L;
      if (!L) return;

      // Calculate center
      const avgLat = locations.reduce((sum, loc) => sum + loc.lat, 0) / locations.length;
      const avgLng = locations.reduce((sum, loc) => sum + loc.lng, 0) / locations.length;

      const osmMap = L.map(mapRef.current!).setView([avgLat, avgLng], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors',
      }).addTo(osmMap);

      // Add markers
      const newMarkers = locations.map((loc) => {
        const marker = (window as any).L.marker([loc.lat, loc.lng]).addTo(osmMap);
        marker.bindTooltip(String(loc.rank), { permanent: true, direction: 'center', className: 'rank-label' });
        if (onPinClick) {
          marker.on('click', () => onPinClick(loc.rank));
        }
        return marker;
      });
      setMarkers(newMarkers);

      // Fit bounds
      const bounds = (window as any).L.latLngBounds(locations.map(l => [(l.lat), (l.lng)]));
      osmMap.fitBounds(bounds, { maxZoom: 15 });
      setMap(osmMap);
    };

    initOsm();
  }, [useOsm, locations, onPinClick]);

  // OSM pan to selected location
  useEffect(() => {
    if (!useOsm || !map || selectedRank === undefined) return;
    const selected = locations.find(l => l.rank === selectedRank);
    if (selected && (map as any).setView) {
      (map as any).setView([selected.lat, selected.lng], 16, { animate: true });
    }
  }, [useOsm, map, selectedRank, locations]);

  function getMarkerColor(decision: string): string {
    switch (decision) {
      case 'MAKE_OFFER':
        return '#16a34a'; // green-600
      case 'NEGOTIATE':
        return '#2563eb'; // blue-600
      case 'PASS':
        return '#9ca3af'; // gray-400
      default:
        return '#9ca3af';
    }
  }

  return (
    <div ref={mapRef} className="w-full h-full rounded-xl shadow-lg" />
  );
}
