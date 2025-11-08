'use client';

import ConfidenceBadge from '@/components/trust/ConfidenceBadge';
import ScoreChip from '@/components/trust/ScoreChip';
import { formatCurrency } from '@/lib/design-system';

interface MetricHeroProps {
  score: number;
  revenueMin: number;
  revenueMax: number;
  confidence: number;
  title?: string;
  subtitle?: string;
  onMethodClick?: () => void;
}

/**
 * MetricHero - Large score + revenue display with confidence badge
 *
 * Hero section showing:
 * - Opportunity score (0-100)
 * - Revenue range (€1.6M - €1.9M)
 * - Confidence badge with tooltip
 */
export default function MetricHero({
  score,
  revenueMin,
  revenueMax,
  confidence,
  title,
  subtitle,
  onMethodClick,
}: MetricHeroProps) {
  const getConfidenceLabel = () => {
    if (confidence >= 0.9) return 'Very high confidence';
    if (confidence >= 0.75) return 'High confidence';
    if (confidence >= 0.6) return 'Medium confidence';
    return 'Limited data';
  };

  return (
    <div className="bg-gradient-to-br from-gradient-50 to-white border border-gradient-100 rounded-2xl p-8 shadow-sm">
      {/* Title/Subtitle (optional) */}
      {title && (
        <div className="mb-6">
          <h1 className="text-3xl font-semibold text-neutral-900">{title}</h1>
          {subtitle && <p className="text-neutral-600 mt-1">{subtitle}</p>}
        </div>
      )}

      <div className="flex items-start gap-8">
        {/* Score Section */}
        <div className="flex-shrink-0">
          <div className="text-sm font-medium text-neutral-600 mb-2">
            Opportunity Score
          </div>
          <div className="flex items-center gap-3">
            <div className="text-6xl font-semibold tabular-nums" style={{ color: score >= 80 ? '#10B981' : score >= 60 ? '#F59E0B' : '#EF4444' }}>
              {Math.round(score)}
            </div>
            <div className="text-3xl font-normal text-neutral-400">/100</div>
          </div>
        </div>

        {/* Divider */}
        <div className="h-24 w-px bg-gradient-200" />

        {/* Revenue Section */}
        <div className="flex-1">
          <div className="text-sm font-medium text-neutral-600 mb-2">
            Predicted Annual Revenue
          </div>
          <div className="text-3xl font-semibold text-neutral-900 mb-3">
            {formatCurrency(revenueMin)} – {formatCurrency(revenueMax)}
          </div>
          <ConfidenceBadge
            confidence={confidence}
            showModal={true}
            onModalClick={onMethodClick}
          />
        </div>
      </div>

      {/* Warning banner for low confidence */}
      {confidence < 0.6 && (
        <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
          <div className="flex items-start gap-2">
            <svg
              className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <div>
              <div className="font-medium text-amber-900">Limited data coverage</div>
              <div className="text-sm text-amber-700 mt-1">
                Confidence {Math.round(confidence * 100)}%. Estimates widen to ±{Math.round((1 - confidence) * 50)}%. Consider alternative areas with higher data coverage.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
