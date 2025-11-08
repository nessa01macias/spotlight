'use client';

import { useState } from 'react';
import { MapPinIcon, CheckCircleIcon, ExclamationCircleIcon, XCircleIcon, EnvelopeIcon } from '@heroicons/react/24/outline';
import { ConfidenceBadge, DataCoverageBar } from '@/components/trust';
import api from '@/lib/api';

interface DecisionCardProps {
  rank: number;
  address: string;
  lat: number;
  lng: number;
  score: number;
  revenue_min_eur: number;
  revenue_max_eur: number;
  confidence: number;
  coverage: {
    demo: number;
    comp: number;
    access: number;
    traffic: number;
    rent: number;
    crime: number;
  };
  why: string[];
  decision: 'MAKE_OFFER' | 'NEGOTIATE' | 'PASS';
  metrics?: Record<string, any>;
  concept?: string;
  onViewDetails?: () => void;
}

export function DecisionCard({
  rank,
  address,
  lat,
  lng,
  score,
  revenue_min_eur,
  revenue_max_eur,
  confidence,
  coverage,
  why,
  decision,
  metrics,
  concept,
  onViewDetails,
}: DecisionCardProps) {
  const [isEmailLoading, setIsEmailLoading] = useState(false);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const handleEmailBroker = async () => {
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

      // Open Gmail with pre-filled draft
      window.open(response.gmail_url, '_blank');
    } catch (error) {
      console.error('Failed to generate broker email:', error);
      alert('Failed to generate email. Please try again.');
    } finally {
      setIsEmailLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 70) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (score >= 50) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getDecisionConfig = (decision: string) => {
    switch (decision) {
      case 'MAKE_OFFER':
        return {
          icon: <CheckCircleIcon className="w-5 h-5" />,
          color: 'bg-green-600 hover:bg-green-700',
          label: 'Make Offer',
          description: 'Strong fundamentals, high confidence',
        };
      case 'NEGOTIATE':
        return {
          icon: <ExclamationCircleIcon className="w-5 h-5" />,
          color: 'bg-blue-600 hover:bg-blue-700',
          label: 'Negotiate',
          description: 'Good potential, verify assumptions',
        };
      case 'PASS':
        return {
          icon: <XCircleIcon className="w-5 h-5" />,
          color: 'bg-neutral-400 hover:bg-neutral-500',
          label: 'Pass',
          description: 'Below threshold or high uncertainty',
        };
      default:
        return {
          icon: <ExclamationCircleIcon className="w-5 h-5" />,
          color: 'bg-neutral-400',
          label: 'Unknown',
          description: '',
        };
    }
  };

  const decisionConfig = getDecisionConfig(decision);
  const coverageData = {
    demographics: coverage.demo,
    competition: coverage.comp,
    transit: coverage.access,
    overall: (coverage.demo + coverage.comp + coverage.access) / 3,
  };

  return (
    <div className="bg-white rounded-xl border-2 border-neutral-200 p-6 shadow-md hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 rounded-full bg-gradient-400 text-white flex items-center justify-center font-bold text-lg">
              {rank}
            </div>
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <MapPinIcon className="w-5 h-5 text-neutral-400" />
              <h3 className="text-lg font-semibold text-neutral-900">{address}</h3>
            </div>
            <p className="text-sm text-neutral-500">
              {lat.toFixed(5)}, {lng.toFixed(5)}
            </p>
          </div>
        </div>
        <div className={`px-4 py-2 rounded-lg font-bold text-xl border-2 ${getScoreColor(score)}`}>
          {score.toFixed(1)}
        </div>
      </div>

      {/* Revenue Prediction */}
      <div className="bg-gradient-50 rounded-lg p-4 border border-gradient-200 mb-4">
        <p className="text-xs font-medium text-neutral-600 mb-1">Predicted Monthly Revenue</p>
        <div className="flex items-baseline gap-2">
          <p className="text-2xl font-bold text-neutral-900">
            {formatCurrency((revenue_min_eur + revenue_max_eur) / 2)}
          </p>
          <p className="text-sm text-neutral-600">
            ({formatCurrency(revenue_min_eur)} - {formatCurrency(revenue_max_eur)})
          </p>
        </div>
      </div>

      {/* Trust Layer */}
      <div className="mb-4 space-y-3">
        <ConfidenceBadge confidence={confidence} />
        <DataCoverageBar coverage={coverageData} />
      </div>

      {/* Why Bullets */}
      <div className="mb-4">
        <p className="text-sm font-medium text-neutral-700 mb-2">Why this location:</p>
        <ul className="space-y-1">
          {why.map((reason, index) => (
            <li key={index} className="flex items-start gap-2 text-sm text-neutral-600">
              <span className="text-gradient-400 font-bold mt-0.5">•</span>
              {reason}
            </li>
          ))}
        </ul>
      </div>

      {/* Action Buttons */}
      <div className="space-y-2">
        {/* Primary Action Row */}
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={handleEmailBroker}
            disabled={isEmailLoading}
            className="px-4 py-3 rounded-lg font-medium text-white bg-gradient-400 hover:bg-gradient-300 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            <EnvelopeIcon className="w-5 h-5" />
            {isEmailLoading ? 'Sending...' : 'Email Broker'}
          </button>
          <button
            onClick={onViewDetails}
            className="px-4 py-3 rounded-lg font-medium text-neutral-700 bg-white border-2 border-neutral-300 hover:border-neutral-400 hover:bg-neutral-50 transition-colors flex items-center justify-center gap-2 shadow-sm"
          >
            <MapPinIcon className="w-5 h-5" />
            View on Map
          </button>
        </div>

        {/* Decision Badge */}
        <div className="flex items-center justify-between p-3 rounded-lg bg-neutral-50 border border-neutral-200">
          <div className="flex items-center gap-2">
            {decisionConfig.icon}
            <span className="font-medium text-neutral-900">{decisionConfig.label}</span>
          </div>
          <span className="text-xs text-neutral-600">{decisionConfig.description}</span>
        </div>
      </div>
    </div>
  );
}
