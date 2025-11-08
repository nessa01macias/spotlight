'use client';

import { CheckCircleIcon, ExclamationTriangleIcon, ArrowRightIcon } from '@heroicons/react/24/outline';

export interface Insight {
  type: 'strength' | 'risk' | 'recommendation';
  text: string;
}

interface InsightListProps {
  insights: Insight[];
  title?: string;
  className?: string;
}

/**
 * InsightList - Bullets with inline numbers, not just checkmarks
 *
 * Shows strengths, risks, and recommendations with:
 * - Inline math (e.g., "28k pop; €48k income +6% vs target")
 * - Color-coded icons
 * - Clean spacing
 */
export default function InsightList({
  insights,
  title,
  className = '',
}: InsightListProps) {
  const getIcon = (type: string) => {
    switch (type) {
      case 'strength':
        return <CheckCircleIcon className="w-5 h-5 text-opportunity-high flex-shrink-0" />;
      case 'risk':
        return <ExclamationTriangleIcon className="w-5 h-5 text-opportunity-medium flex-shrink-0" />;
      case 'recommendation':
        return <ArrowRightIcon className="w-5 h-5 text-gradient-400 flex-shrink-0" />;
      default:
        return null;
    }
  };

  if (insights.length === 0) return null;

  return (
    <div className={className}>
      {title && (
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">{title}</h3>
      )}

      <div className="space-y-3">
        {insights.map((insight, index) => (
          <div key={index} className="flex items-start gap-3">
            {getIcon(insight.type)}
            <p className="text-neutral-700 flex-1 leading-relaxed">
              {insight.text}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
