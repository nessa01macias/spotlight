'use client';

interface DataSource {
  name: string;
  coverage: number;
  color: string;
}

interface Coverage {
  demographics: number;
  competition: number;
  transit: number;
  overall: number;
}

interface DataCoverageBarProps {
  coverage: Coverage;
  className?: string;
}

/**
 * DataCoverageBar - 3-segment inline bar showing data completeness
 *
 * Visualizes coverage across key data sources:
 * - Demographics (PAAVO, Statistics Finland)
 * - Competition (OSM)
 * - Transit access (OSM)
 */
export function DataCoverageBar({
  coverage,
  className = '',
}: DataCoverageBarProps) {
  const sources: DataSource[] = [
    { name: 'Demographics', coverage: coverage.demographics, color: 'bg-emerald-500' },
    { name: 'Competition', coverage: coverage.competition, color: 'bg-blue-500' },
    { name: 'Transit', coverage: coverage.transit, color: 'bg-purple-500' },
  ];

  const averageCoverage = coverage.overall;

  return (
    <div className={`${className}`}>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-sm font-medium text-neutral-700">Data Coverage</span>
        <span className="text-sm text-neutral-500">
          {Math.round(averageCoverage * 100)}%
        </span>
      </div>

      {/* Coverage bars */}
      <div className="space-y-2">
        {sources.map((source) => (
          <div key={source.name} className="flex items-center gap-2">
            <div className="w-24 text-xs text-neutral-600">{source.name}</div>
            <div className="flex-1 h-2 bg-neutral-100 rounded-full overflow-hidden">
              <div
                className={`h-full ${source.color} transition-all duration-300 ease-out`}
                style={{ width: `${source.coverage * 100}%` }}
              />
            </div>
            <div className="w-12 text-right text-xs text-neutral-500">
              {Math.round(source.coverage * 100)}%
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
