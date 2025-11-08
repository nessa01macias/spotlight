'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import api from '@/lib/api';
import { Concept } from '@/lib/types';
import { grainTexture } from '@/lib/design-system';
import {
  ArrowLeftIcon,
  MapPinIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import { ConfidenceBadge, DataCoverageBar } from '@/components/trust';

interface AreaDetailData {
  area_id: string;
  area_name: string;
  city: string;
  score: number;
  predicted_revenue_low: number;
  predicted_revenue_mid: number;
  predicted_revenue_high: number;
  confidence: number;
  coverage: {
    demographics: number;
    competition: number;
    transit: number;
    overall: number;
  };
  method: {
    scoring_method: string;
    data_sources: string[];
    last_updated: string;
    confidence_basis: string;
  };
  why: string[];
  demographics: any;
  competition_analysis: any;
  traffic_access: any;
  latitude: number;
  longitude: number;
  strengths: string[];
  risks: string[];
  nearby_alternatives: any[];
}

export default function AreaDetailPage({ params }: { params: { id: string } }) {
  const areaId = params.id;
  const searchParams = useSearchParams();
  const router = useRouter();

  // Validate concept parameter is present
  const conceptParam = searchParams.get('concept');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<AreaDetailData | null>(null);

  useEffect(() => {
    const fetchAreaDetail = async () => {
      // Check for missing concept parameter
      if (!conceptParam) {
        setError('Concept parameter missing. Please return to discovery and select a concept.');
        setLoading(false);
        return;
      }

      const concept = conceptParam as Concept;
      setLoading(true);
      setError(null);

      try {
        const result = await api.getAreaDetail(areaId, concept);
        setData(result);
      } catch (err: any) {
        console.error('Area detail error:', err);
        setError(err.response?.data?.detail || 'Failed to load area details');
      } finally {
        setLoading(false);
      }
    };

    fetchAreaDetail();
  }, [areaId, conceptParam]);

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
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 transition-colors"
          >
            <ArrowLeftIcon className="w-5 h-5" />
            <span className="font-medium">Back to Discovery</span>
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center space-y-4">
              <div className="w-12 h-12 border-4 border-gradient-200 border-t-gradient-400 rounded-full animate-spin mx-auto" />
              <p className="text-neutral-600">Loading area details...</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-red-900 mb-2">Error</h3>
            <p className="text-red-700">{error}</p>
            <button
              onClick={() => router.back()}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Go Back
            </button>
          </div>
        )}

        {/* Content */}
        {data && !loading && (
          <div className="space-y-6">
            {/* Hero Section */}
            <div className="bg-white rounded-xl border border-neutral-200 p-8 shadow-sm">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <MapPinIcon className="w-6 h-6 text-gradient-400" />
                    <h1 className="text-3xl font-bold text-neutral-900">{data.area_name}</h1>
                  </div>
                  <p className="text-neutral-600">{data.city}</p>
                </div>
                <div
                  className={`px-6 py-3 rounded-lg font-bold text-2xl border ${getScoreColor(
                    data.score
                  )}`}
                >
                  {data.score.toFixed(1)}
                </div>
              </div>

              {/* Trust Layer */}
              <div className="flex items-center gap-6 mb-6">
                <ConfidenceBadge confidence={data.confidence} />
                <div className="flex-1">
                  <DataCoverageBar coverage={data.coverage} />
                </div>
              </div>

              {/* Revenue Prediction */}
              <div className="bg-gradient-50 rounded-lg p-6 border border-gradient-200">
                <h3 className="text-sm font-medium text-neutral-600 mb-2">
                  Predicted Annual Revenue
                </h3>
                <div className="flex items-baseline gap-3">
                  <p className="text-3xl font-bold text-neutral-900">
                    {formatCurrency(data.predicted_revenue_mid * 12)}
                  </p>
                  <p className="text-neutral-600">
                    ({formatCurrency(data.predicted_revenue_low * 12)} -{' '}
                    {formatCurrency(data.predicted_revenue_high * 12)})
                  </p>
                </div>
              </div>
            </div>

            {/* Why This Area Works */}
            <div className="bg-white rounded-xl border border-neutral-200 p-6 shadow-sm">
              <h2 className="text-xl font-bold text-neutral-900 mb-4">
                Why This Area Scores {data.score.toFixed(0)}/100
              </h2>
              <ul className="space-y-3">
                {data.why.map((reason, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-gradient-100 text-gradient-400 flex items-center justify-center text-sm font-bold mt-0.5">
                      {index + 1}
                    </div>
                    <p className="text-neutral-700 flex-1">{reason}</p>
                  </li>
                ))}
              </ul>
            </div>

            {/* Detailed Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Demographics */}
              <div className="bg-white rounded-xl border border-neutral-200 p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Demographics</h3>
                <dl className="space-y-3">
                  {data.demographics.population_1km && (
                    <div>
                      <dt className="text-sm text-neutral-600">Population (1km)</dt>
                      <dd className="text-lg font-semibold text-neutral-900">
                        {data.demographics.population_1km.toLocaleString()}
                      </dd>
                    </div>
                  )}
                  {data.demographics.median_income && (
                    <div>
                      <dt className="text-sm text-neutral-600">Median Income</dt>
                      <dd className="text-lg font-semibold text-neutral-900">
                        {formatCurrency(data.demographics.median_income)}/year
                      </dd>
                    </div>
                  )}
                  {data.demographics.population_density && (
                    <div>
                      <dt className="text-sm text-neutral-600">Density</dt>
                      <dd className="text-lg font-semibold text-neutral-900">
                        {Math.round(data.demographics.population_density).toLocaleString()}/km²
                      </dd>
                    </div>
                  )}
                </dl>
              </div>

              {/* Competition */}
              <div className="bg-white rounded-xl border border-neutral-200 p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Competition</h3>
                <dl className="space-y-3">
                  {data.competition_analysis.competitors_count !== undefined && (
                    <div>
                      <dt className="text-sm text-neutral-600">Competitors Nearby</dt>
                      <dd className="text-lg font-semibold text-neutral-900">
                        {data.competition_analysis.competitors_count}
                      </dd>
                    </div>
                  )}
                  {data.competition_analysis.competitors_per_1k_residents && (
                    <div>
                      <dt className="text-sm text-neutral-600">Per 1k Residents</dt>
                      <dd className="text-lg font-semibold text-neutral-900">
                        {data.competition_analysis.competitors_per_1k_residents.toFixed(2)}
                      </dd>
                    </div>
                  )}
                </dl>
              </div>

              {/* Transit & Access */}
              <div className="bg-white rounded-xl border border-neutral-200 p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Transit & Access</h3>
                <dl className="space-y-3">
                  {data.traffic_access.nearest_metro_distance_m && (
                    <div>
                      <dt className="text-sm text-neutral-600">Nearest Metro</dt>
                      <dd className="text-lg font-semibold text-neutral-900">
                        {Math.round(data.traffic_access.nearest_metro_distance_m)}m
                      </dd>
                    </div>
                  )}
                  {data.traffic_access.nearest_tram_distance_m && (
                    <div>
                      <dt className="text-sm text-neutral-600">Nearest Tram</dt>
                      <dd className="text-lg font-semibold text-neutral-900">
                        {Math.round(data.traffic_access.nearest_tram_distance_m)}m
                      </dd>
                    </div>
                  )}
                  {data.traffic_access.walkability_poi_count !== undefined && (
                    <div>
                      <dt className="text-sm text-neutral-600">Walkability POIs</dt>
                      <dd className="text-lg font-semibold text-neutral-900">
                        {data.traffic_access.walkability_poi_count}
                      </dd>
                    </div>
                  )}
                </dl>
              </div>
            </div>

            {/* Strengths & Risks */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Strengths */}
              <div className="bg-white rounded-xl border border-neutral-200 p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
                  <CheckCircleIcon className="w-5 h-5 text-green-600" />
                  Key Strengths
                </h3>
                <ul className="space-y-2">
                  {data.strengths.map((strength, index) => (
                    <li key={index} className="text-neutral-700 flex items-start gap-2">
                      <span className="text-green-600 font-bold">✓</span>
                      {strength}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Risks */}
              <div className="bg-white rounded-xl border border-neutral-200 p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
                  <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600" />
                  Key Risks
                </h3>
                <ul className="space-y-2">
                  {data.risks.map((risk, index) => (
                    <li key={index} className="text-neutral-700 flex items-start gap-2">
                      <span className="text-yellow-600 font-bold">⚠</span>
                      {risk}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Method Transparency */}
            <div className="bg-neutral-50 rounded-xl border border-neutral-200 p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4">How This Was Calculated</h3>
              <div className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-neutral-600">Method:</span>
                  <span className="ml-2 text-neutral-900">
                    {data.method.scoring_method === 'heuristic'
                      ? 'Heuristic Scoring'
                      : 'Agent-Based Analysis'}
                  </span>
                </div>
                <div>
                  <span className="text-sm font-medium text-neutral-600">Data Sources:</span>
                  <ul className="ml-2 mt-1 space-y-1">
                    {data.method.data_sources.map((source, index) => (
                      <li key={index} className="text-sm text-neutral-700">
                        • {source}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <span className="text-sm font-medium text-neutral-600">Confidence Basis:</span>
                  <span className="ml-2 text-neutral-700">{data.method.confidence_basis}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-neutral-600">Last Updated:</span>
                  <span className="ml-2 text-neutral-700">
                    {new Date(data.method.last_updated).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

