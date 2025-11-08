'use client';

import { getScoreColor } from '@/lib/design-system';

interface ScoreChipProps {
  score: number;
  maxScore?: number;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

/**
 * ScoreChip - Large numeral pill showing opportunity score
 *
 * Color-coded by score threshold:
 * - ≥80: Green (high opportunity)
 * - 60-79: Amber (medium opportunity)
 * - <60: Red (low opportunity)
 */
export default function ScoreChip({
  score,
  maxScore = 100,
  size = 'md',
  className = '',
}: ScoreChipProps) {
  const color = getScoreColor(score);

  // Get background color based on score
  const getBgColor = () => {
    if (score >= 80) return 'bg-emerald-50';
    if (score >= 60) return 'bg-amber-50';
    return 'bg-red-50';
  };

  const getTextColor = () => {
    if (score >= 80) return 'text-opportunity-high';
    if (score >= 60) return 'text-opportunity-medium';
    return 'text-opportunity-low';
  };

  const getBorderColor = () => {
    if (score >= 80) return 'border-opportunity-high/20';
    if (score >= 60) return 'border-opportunity-medium/20';
    return 'border-opportunity-low/20';
  };

  const sizeClasses = {
    sm: 'px-2.5 py-1 text-sm',
    md: 'px-3 py-1.5 text-base',
    lg: 'px-4 py-2 text-lg',
  };

  return (
    <div
      className={`
        inline-flex items-center justify-center
        font-semibold rounded-full border
        ${getBgColor()}
        ${getTextColor()}
        ${getBorderColor()}
        ${sizeClasses[size]}
        ${className}
      `}
    >
      <span className="tabular-nums">
        {Math.round(score)}
        <span className="text-neutral-500 font-normal">/{maxScore}</span>
      </span>
    </div>
  );
}
