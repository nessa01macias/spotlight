'use client';

import { useState } from 'react';
import { MapPinIcon, CheckCircleIcon, ExclamationCircleIcon, XCircleIcon, EnvelopeIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import api from '@/lib/api';
import { ProvenanceTooltip } from './ProvenanceTooltip';

interface MetricProvenance {
  score: number;
  weight: number;
  weighted_score: number;
  source: string;
  coverage: number;
  raw_value?: number | null;
  raw_unit?: string | null;
}

interface ScoreProvenance {
  population: MetricProvenance;
  income_fit: MetricProvenance;
  transit_access: MetricProvenance;
  competition_inverse: MetricProvenance;
  traffic_access: MetricProvenance;
  crime_penalty_cap?: MetricProvenance;
  total_score: number;
  confidence_basis: string;
}

interface AddressListItemProps {
  rank: number;
  address: string;
  lat: number;
  lng: number;
  score: number;
  revenue_min_eur: number;
  revenue_max_eur: number;
  confidence: number;
  decision: 'MAKE_OFFER' | 'NEGOTIATE' | 'PASS';
  decision_reasoning?: string;
  why: string[];
  provenance?: ScoreProvenance;
  concept?: string;
  isSelected?: boolean;
  onClick?: () => void;
}

export function AddressListItem({
  rank,
  address,
  lat,
  lng,
  score,
  revenue_min_eur,
  revenue_max_eur,
  confidence,
  decision,
  decision_reasoning,
  why,
  provenance,
  concept,
  isSelected,
  onClick,
}: AddressListItemProps) {
  const [isEmailLoading, setIsEmailLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const handleEmailBroker = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card selection
    if (!concept) {
      alert('Concept is required to generate broker email');
      return;
    }

    setIsEmailLoading(true);
    try {
      const response = await api.pursueAddress(
        address,
        lat,
        lng,
        concept,
        score,
        revenue_min_eur,
        revenue_max_eur,
        why
      );
      window.open(response.gmail_url, '_blank');
    } catch (error) {
      console.error('Failed to generate broker email:', error);
      alert('Failed to generate email. Please try again.');
    } finally {
      setIsEmailLoading(false);
    }
  };

  const handleStreetView = (e: React.MouseEvent) => {
    e.stopPropagation();
    const streetViewUrl = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lng}`;
    window.open(streetViewUrl, '_blank');
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600 bg-green-50';
    if (score >= 70) return 'text-blue-600 bg-blue-50';
    if (score >= 50) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getDecisionConfig = (decision: string) => {
    switch (decision) {
      case 'MAKE_OFFER':
        return {
          icon: <CheckCircleIcon className="w-4 h-4" />,
          color: 'text-green-700 bg-green-50',
          label: 'Make Offer',
        };
      case 'NEGOTIATE':
        return {
          icon: <ExclamationCircleIcon className="w-4 h-4" />,
          color: 'text-blue-700 bg-blue-50',
          label: 'Negotiate',
        };
      case 'PASS':
        return {
          icon: <XCircleIcon className="w-4 h-4" />,
          color: 'text-neutral-600 bg-neutral-50',
          label: 'Pass',
        };
      default:
        return {
          icon: <ExclamationCircleIcon className="w-4 h-4" />,
          color: 'text-neutral-600 bg-neutral-50',
          label: 'Unknown',
        };
    }
  };

  const decisionConfig = getDecisionConfig(decision);

  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-lg border-2 p-4 cursor-pointer transition-all hover:shadow-md ${
        isSelected ? 'border-gradient-400 shadow-lg ring-2 ring-gradient-200' : 'border-neutral-200'
      }`}
    >
      {/* Header */}
      <div className="flex items-start gap-3 mb-3">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-gradient-400 text-white flex items-center justify-center font-bold text-sm">
            {rank}
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h3 className="text-sm font-semibold text-neutral-900 truncate">{address}</h3>
            <div className="flex items-center gap-1">
              <div className={`px-2 py-1 rounded font-bold text-sm ${getScoreColor(score)}`}>
                {score.toFixed(1)}
              </div>
              {provenance && (
                <ProvenanceTooltip
                  provenance={provenance}
                  decision_reasoning={decision_reasoning}
                />
              )}
            </div>
          </div>
          <div className="flex items-center gap-2 mt-1">
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${decisionConfig.color}`}>
              {decisionConfig.icon}
              {decisionConfig.label}
            </span>
            <span className="text-xs text-neutral-500">
              {(confidence * 100).toFixed(0)}% confidence
            </span>
          </div>
          {decision_reasoning && !provenance && (
            <p className="text-xs text-neutral-500 mt-1 italic">{decision_reasoning}</p>
          )}
        </div>
      </div>

      {/* Revenue */}
      <div className="bg-gradient-50 rounded px-3 py-2 mb-3">
        <p className="text-xs text-neutral-600 mb-0.5">Revenue</p>
        <p className="text-lg font-bold text-neutral-900">
          {formatCurrency((revenue_min_eur + revenue_max_eur) / 2)}/mo
        </p>
      </div>

      {/* Expandable Provenance Details */}
      {provenance && (
        <div className="mb-3">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
            className="w-full flex items-center justify-between text-xs text-neutral-600 hover:text-neutral-900 transition-colors py-2"
          >
            <span className="font-medium">View score breakdown</span>
            {isExpanded ? (
              <ChevronUpIcon className="w-4 h-4" />
            ) : (
              <ChevronDownIcon className="w-4 h-4" />
            )}
          </button>

          {isExpanded && (
            <div className="bg-neutral-50 rounded p-3 space-y-2">
              {/* Weight distribution visualization */}
              <div className="mb-3">
                <p className="text-xs font-semibold text-neutral-700 mb-2">Score Components</p>
                <div className="space-y-1.5">
                  {[
                    { key: 'population', label: 'Population', metric: provenance.population },
                    { key: 'income_fit', label: 'Income Fit', metric: provenance.income_fit },
                    { key: 'transit_access', label: 'Transit', metric: provenance.transit_access },
                    { key: 'competition_inverse', label: 'Competition', metric: provenance.competition_inverse },
                    { key: 'traffic_access', label: 'Traffic', metric: provenance.traffic_access },
                  ].map(({ key, label, metric }) => (
                    <div key={key}>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-neutral-600">{label}</span>
                        <span className="font-bold text-neutral-900">
                          {metric.weighted_score.toFixed(1)}
                        </span>
                      </div>
                      <div className="w-full bg-neutral-200 rounded-full h-1.5 overflow-hidden">
                        <div
                          className="bg-gradient-400 h-full transition-all"
                          style={{ width: `${(metric.weighted_score / provenance.total_score) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Data sources */}
              <div className="border-t border-neutral-200 pt-2">
                <p className="text-xs font-semibold text-neutral-700 mb-1">Data Sources</p>
                <div className="space-y-1">
                  {Array.from(new Set([
                    provenance.population.source,
                    provenance.transit_access.source,
                    provenance.competition_inverse.source,
                  ])).map((source, idx) => (
                    <div key={idx} className="flex items-start gap-1 text-xs text-neutral-500">
                      <span className="text-neutral-400">•</span>
                      <span className="flex-1">{source}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={handleEmailBroker}
          disabled={isEmailLoading}
          className="px-3 py-2 rounded font-medium text-sm text-white bg-gradient-400 hover:bg-gradient-300 transition-colors flex items-center justify-center gap-1.5 disabled:opacity-50"
        >
          <EnvelopeIcon className="w-4 h-4" />
          Email
        </button>
        <button
          onClick={handleStreetView}
          className="px-3 py-2 rounded font-medium text-sm text-neutral-700 bg-neutral-100 hover:bg-neutral-200 transition-colors flex items-center justify-center gap-1.5"
        >
          <MapPinIcon className="w-4 h-4" />
          Street View
        </button>
      </div>
    </div>
  );
}
