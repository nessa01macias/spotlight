'use client';

import ScoreChip from '@/components/trust/ScoreChip';
import Button from '@/components/ui/Button';
import { formatCurrency } from '@/lib/design-system';
import { ChevronRightIcon } from '@heroicons/react/24/outline';

interface OpportunityCardProps {
  name: string;
  score: number;
  revenueMin: number;
  revenueMax: number;
  confidence?: number;
  onView: () => void;
  onCompare?: () => void;
  className?: string;
}

/**
 * OpportunityCard - Clean card for discovery view sidebar
 *
 * Shows:
 * - Area name
 * - Score chip (right-aligned)
 * - Revenue range (muted text)
 * - Max 2 CTAs (View + Compare)
 */
export default function OpportunityCard({
  name,
  score,
  revenueMin,
  revenueMax,
  confidence,
  onView,
  onCompare,
  className = '',
}: OpportunityCardProps) {
  return (
    <div
      className={`
        bg-white border border-gradient-100 rounded-lg p-6
        shadow-sm hover:shadow-md hover:border-gradient-200
        transition-all duration-150 ease-out
        ${className}
      `}
    >
      {/* Header: Name + Score */}
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-neutral-900 flex-1 pr-4">
          {name}
        </h3>
        <ScoreChip score={score} size="md" />
      </div>

      {/* Revenue Range */}
      <div className="text-neutral-600 mb-4">
        <span className="text-base">
          {formatCurrency(revenueMin)} – {formatCurrency(revenueMax)}
        </span>
        {confidence && (
          <span className="text-sm text-neutral-500 ml-2">
            ({confidence >= 0.75 ? 'High' : confidence >= 0.6 ? 'Medium' : 'Low'} confidence)
          </span>
        )}
      </div>

      {/* Actions (max 2) */}
      <div className="flex items-center gap-2">
        <Button variant="primary" size="sm" onClick={onView} className="flex-1">
          View
          <ChevronRightIcon className="w-4 h-4 ml-1" />
        </Button>
        {onCompare && (
          <Button variant="secondary" size="sm" onClick={onCompare}>
            Compare
          </Button>
        )}
      </div>
    </div>
  );
}
