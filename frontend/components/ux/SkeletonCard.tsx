'use client';

interface SkeletonCardProps {
  variant?: 'card' | 'hero' | 'list';
  count?: number;
  className?: string;
}

/**
 * SkeletonCard - Loading states (no spinners)
 *
 * Provides skeleton loading for:
 * - Cards (OpportunityCard style)
 * - Hero (MetricHero style)
 * - List items
 */
export default function SkeletonCard({
  variant = 'card',
  count = 1,
  className = '',
}: SkeletonCardProps) {
  const skeletons = Array.from({ length: count });

  if (variant === 'hero') {
    return (
      <div className={`bg-gradient-50 border border-gradient-100 rounded-2xl p-8 ${className}`}>
        <div className="animate-pulse">
          <div className="flex items-start gap-8">
            <div className="flex-shrink-0">
              <div className="h-4 w-32 bg-gradient-200 rounded mb-4"></div>
              <div className="h-16 w-32 bg-gradient-200 rounded"></div>
            </div>
            <div className="h-24 w-px bg-gradient-200" />
            <div className="flex-1">
              <div className="h-4 w-48 bg-gradient-200 rounded mb-4"></div>
              <div className="h-10 w-64 bg-gradient-200 rounded mb-4"></div>
              <div className="h-8 w-40 bg-gradient-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'list') {
    return (
      <div className={`space-y-3 ${className}`}>
        {skeletons.map((_, i) => (
          <div key={i} className="animate-pulse flex items-start gap-3">
            <div className="w-5 h-5 bg-gradient-200 rounded-full flex-shrink-0"></div>
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gradient-200 rounded w-full"></div>
              <div className="h-4 bg-gradient-200 rounded w-3/4"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Default: card variant
  return (
    <div className={`space-y-4 ${className}`}>
      {skeletons.map((_, i) => (
        <div
          key={i}
          className="bg-white border border-gradient-100 rounded-lg p-6 shadow-sm"
        >
          <div className="animate-pulse">
            <div className="flex items-start justify-between mb-3">
              <div className="h-6 w-40 bg-gradient-200 rounded"></div>
              <div className="h-8 w-16 bg-gradient-200 rounded-full"></div>
            </div>
            <div className="h-4 w-48 bg-gradient-200 rounded mb-4"></div>
            <div className="flex items-center gap-2">
              <div className="h-9 flex-1 bg-gradient-200 rounded-lg"></div>
              <div className="h-9 w-24 bg-gradient-200 rounded-lg"></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
