'use client';

import { useState } from 'react';
import { InformationCircleIcon } from '@heroicons/react/24/outline';

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

interface ProvenanceTooltipProps {
  provenance: ScoreProvenance;
  decision_reasoning?: string;
}

export function ProvenanceTooltip({ provenance, decision_reasoning }: ProvenanceTooltipProps) {
  const [isOpen, setIsOpen] = useState(false);

  const metrics = [
    { key: 'population', label: 'Population Density', emoji: '👥' },
    { key: 'income_fit', label: 'Income Fit', emoji: '💰' },
    { key: 'transit_access', label: 'Transit Access', emoji: '🚇' },
    { key: 'competition_inverse', label: 'Competition (inverse)', emoji: '🏪' },
    { key: 'traffic_access', label: 'Traffic Access', emoji: '🚗' },
  ] as const;

  const getCoverageColor = (coverage: number) => {
    if (coverage >= 0.8) return 'text-green-600';
    if (coverage >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getCoverageLabel = (coverage: number) => {
    if (coverage >= 0.8) return 'High';
    if (coverage >= 0.5) return 'Medium';
    return 'Low';
  };

  return (
    <div className="relative inline-block">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        onBlur={() => setTimeout(() => setIsOpen(false), 200)}
        className="inline-flex items-center justify-center w-5 h-5 rounded-full hover:bg-neutral-100 transition-colors"
        aria-label="Show score provenance"
      >
        <InformationCircleIcon className="w-4 h-4 text-neutral-400 hover:text-neutral-600" />
      </button>

      {isOpen && (
        <div className="absolute z-50 right-0 mt-2 w-96 bg-white rounded-lg shadow-xl border-2 border-neutral-200 p-4">
          <div className="mb-3">
            <h4 className="text-sm font-bold text-neutral-900 mb-1">Score Breakdown</h4>
            <p className="text-xs text-neutral-600">{provenance.confidence_basis}</p>
          </div>

          {/* Metrics table */}
          <div className="space-y-2 mb-4">
            {metrics.map(({ key, label, emoji }) => {
              const metric = provenance[key];
              if (!metric) return null;

              return (
                <div key={key} className="bg-neutral-50 rounded p-2">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-medium text-neutral-700">
                      {emoji} {label}
                    </span>
                    <span className="text-xs font-bold text-neutral-900">
                      {metric.weighted_score.toFixed(1)} pts
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-neutral-500">
                    <span>
                      {metric.score.toFixed(0)}/100 × {(metric.weight * 100).toFixed(0)}% weight
                    </span>
                    <span className={getCoverageColor(metric.coverage)}>
                      {getCoverageLabel(metric.coverage)} data
                    </span>
                  </div>
                  <div className="mt-1 text-xs text-neutral-400 truncate" title={metric.source}>
                    📊 {metric.source}
                  </div>
                  {metric.raw_value !== null && metric.raw_value !== undefined && (
                    <div className="mt-1 text-xs text-neutral-500">
                      🔢 {metric.raw_value.toLocaleString()} {metric.raw_unit}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Total */}
          <div className="border-t-2 border-neutral-200 pt-3 mb-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-neutral-900">Total Score</span>
              <span className="text-lg font-bold text-gradient-400">
                {provenance.total_score.toFixed(1)}
              </span>
            </div>
          </div>

          {/* Decision reasoning */}
          {decision_reasoning && (
            <div className="bg-blue-50 border border-blue-200 rounded p-2">
              <p className="text-xs text-blue-900">{decision_reasoning}</p>
            </div>
          )}

          {/* Data sources footer */}
          <div className="mt-3 pt-3 border-t border-neutral-200">
            <p className="text-xs text-neutral-400 italic">
              All scores backed by public data sources. Tap metric for details.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
