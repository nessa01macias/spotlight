'use client';

import { InformationCircleIcon } from '@heroicons/react/24/outline';
import { getConfidenceColor, formatConfidence, getConfidenceBand } from '@/lib/design-system';
import { useState } from 'react';

interface ConfidenceBadgeProps {
  confidence: number;
  dataCoverage?: number;
  className?: string;
  showModal?: boolean;
  onModalClick?: () => void;
}

/**
 * ConfidenceBadge - Color-coded confidence indicator with tooltip
 *
 * Shows confidence score with appropriate color based on threshold:
 * - <0.6: Amber (low confidence)
 * - 0.6-0.75: Green (medium confidence)
 * - 0.75-0.9: Emerald (high confidence)
 * - >0.9: Dark emerald (very high confidence)
 */
export function ConfidenceBadge({
  confidence,
  dataCoverage = 0.85,
  className = '',
  showModal = true,
  onModalClick,
}: ConfidenceBadgeProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  const color = getConfidenceColor(confidence);
  const { value } = formatConfidence(confidence);
  const band = getConfidenceBand(confidence);
  const coveragePercent = Math.round(dataCoverage * 100);

  // Get text color class based on confidence
  const getTextColor = () => {
    if (confidence < 0.6) return 'text-confidence-low';
    if (confidence < 0.75) return 'text-confidence-medium';
    if (confidence < 0.9) return 'text-confidence-high';
    return 'text-confidence-veryHigh';
  };

  const getBgColor = () => {
    if (confidence < 0.6) return 'bg-amber-50';
    if (confidence < 0.75) return 'bg-emerald-50';
    if (confidence < 0.9) return 'bg-emerald-100';
    return 'bg-emerald-100';
  };

  const getBorderColor = () => {
    if (confidence < 0.6) return 'border-confidence-low/20';
    if (confidence < 0.75) return 'border-confidence-medium/20';
    if (confidence < 0.9) return 'border-confidence-high/20';
    return 'border-confidence-veryHigh/20';
  };

  return (
    <div className={`relative inline-flex items-center gap-1.5 ${className}`}>
      <div
        className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border ${getBgColor()} ${getBorderColor()}`}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <span className={`text-sm font-medium ${getTextColor()}`}>
          Confidence {value}
        </span>

        {showModal && (
          <button
            onClick={onModalClick}
            className={`${getTextColor()} hover:opacity-70 transition-opacity`}
            aria-label="Learn how we calculate confidence"
          >
            <InformationCircleIcon className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Tooltip */}
      {showTooltip && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 pointer-events-none">
          <div className="bg-neutral-900 text-white text-sm rounded-lg px-3 py-2 shadow-lg max-w-xs">
            <p className="font-medium mb-1">
              Confidence {value} — {confidence >= 0.75 ? 'high' : confidence >= 0.6 ? 'medium' : 'low'} data coverage
            </p>
            <p className="text-neutral-300 text-xs">
              Based on population, income, transit, competition. Data coverage: {coveragePercent}%. Estimate band ±{band}%.
            </p>
            {/* Arrow */}
            <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-px">
              <div className="border-8 border-transparent border-t-neutral-900"></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
