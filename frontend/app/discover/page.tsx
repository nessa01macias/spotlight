'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import api from '@/lib/api';
import { grainTexture } from '@/lib/design-system';
import { ArrowLeftIcon, MapPinIcon } from '@heroicons/react/24/outline';

interface AreaOpportunity {
  area_id: string;
  area_name: string;
  score: number;
  latitude: number;
  longitude: number;
  predicted_revenue_low: number;
  predicted_revenue_high: number;
  estimated_rent_psqft?: number;
  available_properties_count?: number;
}

interface DiscoveryResult {
  city: string;
  concept: string;
  heatmap_data: any[];
  top_opportunities: AreaOpportunity[];
  total_areas_scored: number;
}

function DiscoverContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const city = searchParams.get('city') || '';
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DiscoveryResult | null>(null);
  const [selectedConcept, setSelectedConcept] = useState('CasualDining');

  const concepts = [
    { id: 'QSR', name: 'Quick Service' },
    { id: 'FastCasual', name: 'Fast Casual' },
    { id: 'Coffee', name: 'Coffee Shop' },
    { id: 'CasualDining', name: 'Casual Dining' },
    { id: 'FineDining', name: 'Fine Dining' },
  ];

  useEffect(() => {
    if (!city) {
      setError('No city specified');
      setLoading(false);
      return;
    }

    const fetchDiscovery = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await api.discover(city, selectedConcept as any);
        setResult(data);
      } catch (err: any) {
        console.error('Discovery error:', err);
        setError(err.response?.data?.detail || 'Failed to load discovery data');
      } finally {
        setLoading(false);
      }
    };

    fetchDiscovery();
  }, [city, selectedConcept]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 60) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  return (
    <div
      className="min-h-screen bg-gradient-to-br from-gradient-50 via-white to-gradient-100"
      style={grainTexture}
    >
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-neutral-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => router.push('/')}
              className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 transition-colors"
            >
              <ArrowLeftIcon className="w-5 h-5" />
              <span className="font-medium">Back to Search</span>
            </button>
            <div className="flex items-center gap-2">
              <MapPinIcon className="w-5 h-5 text-gradient-400" />
              <h1 className="text-xl font-semibold text-neutral-900">
                {result?.city || city}
              </h1>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Concept Selector */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-neutral-700 mb-3">
            Select Restaurant Concept
          </label>
          <div className="flex gap-3 flex-wrap">
            {concepts.map((concept) => (
              <button
                key={concept.id}
                onClick={() => setSelectedConcept(concept.id)}
                className={`
                  px-4 py-2 rounded-lg font-medium transition-all duration-150
                  ${
                    selectedConcept === concept.id
                      ? 'bg-gradient-400 text-white shadow-md'
                      : 'bg-white text-neutral-700 border border-neutral-200 hover:border-gradient-300'
                  }
                `}
              >
                {concept.name}
              </button>
            ))}
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center space-y-4">
              <div className="w-12 h-12 border-4 border-gradient-200 border-t-gradient-400 rounded-full animate-spin mx-auto" />
              <p className="text-neutral-600">Analyzing opportunities...</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-red-900 mb-2">Error</h3>
            <p className="text-red-700">{error}</p>
            <button
              onClick={() => router.push('/')}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Back to Home
            </button>
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="space-y-6">
            {/* Stats */}
            <div className="bg-white rounded-xl border border-neutral-200 p-6 shadow-sm">
              <div className="flex items-baseline justify-between">
                <div>
                  <p className="text-sm text-neutral-600">Areas Analyzed</p>
                  <p className="text-3xl font-bold text-neutral-900">
                    {result.total_areas_scored}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-neutral-600">Concept</p>
                  <p className="text-lg font-semibold text-gradient-400">
                    {concepts.find((c) => c.id === selectedConcept)?.name}
                  </p>
                </div>
              </div>
            </div>

            {/* Top Opportunities */}
            <div>
              <h2 className="text-2xl font-bold text-neutral-900 mb-4">
                Top Opportunities
              </h2>
              <div className="space-y-4">
                {result.top_opportunities.map((area, index) => (
                  <button
                    key={area.area_id}
                    onClick={() => router.push(`/area/${area.area_id}?concept=${selectedConcept}`)}
                    className="w-full text-left bg-white rounded-xl border border-neutral-200 p-6 shadow-sm hover:shadow-md hover:border-gradient-300 transition-all cursor-pointer"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-start gap-4">
                        <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-100 text-gradient-400 font-bold text-lg">
                          #{index + 1}
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-neutral-900">
                            {area.area_name}
                          </h3>
                          <p className="text-sm text-neutral-600 mt-1">
                            Lat: {area.latitude.toFixed(4)}, Lng: {area.longitude.toFixed(4)}
                          </p>
                          {/* Trust indicators */}
                          {area.confidence !== undefined && (
                            <div className="mt-2 flex items-center gap-2">
                              <span className="text-xs text-neutral-500">
                                Confidence: {Math.round(area.confidence * 100)}%
                              </span>
                              <span className="text-xs text-neutral-400">•</span>
                              <span className="text-xs text-neutral-500">
                                Coverage: {Math.round((area.coverage?.overall || 0) * 100)}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                      <div
                        className={`px-4 py-2 rounded-lg font-bold text-lg border ${getScoreColor(
                          area.score
                        )}`}
                      >
                        {area.score.toFixed(1)}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-neutral-100">
                      <div>
                        <p className="text-sm text-neutral-600">Predicted Revenue</p>
                        <p className="text-lg font-semibold text-neutral-900">
                          {formatCurrency(area.predicted_revenue_low)} -{' '}
                          {formatCurrency(area.predicted_revenue_high)}
                        </p>
                      </div>
                      {area.estimated_rent_psqft && area.estimated_rent_psqft > 0 && (
                        <div>
                          <p className="text-sm text-neutral-600">Est. Rent</p>
                          <p className="text-lg font-semibold text-neutral-900">
                            €{area.estimated_rent_psqft}/sqft
                          </p>
                        </div>
                      )}
                    </div>
                    
                    <div className="mt-4 flex items-center justify-end">
                      <span className="text-sm text-gradient-400 font-medium">
                        View Details →
                      </span>
                    </div>
                  </button>
                ))}
              </div>

              {result.top_opportunities.length === 0 && (
                <div className="bg-neutral-50 rounded-xl p-8 text-center">
                  <p className="text-neutral-600">No opportunities found</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function DiscoverPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <div className="w-12 h-12 border-4 border-gradient-200 border-t-gradient-400 rounded-full animate-spin" />
        </div>
      }
    >
      <DiscoverContent />
    </Suspense>
  );
}

