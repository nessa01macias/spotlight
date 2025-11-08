'use client';

import ScoreChip from '@/components/trust/ScoreChip';
import { formatCurrency, formatArea } from '@/lib/design-system';
import {
  ArrowUpIcon,
  ArrowDownIcon,
  MinusIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

export interface ComparisonSite {
  id: string;
  name: string;
  score: number;
  population: number;
  income: number;
  transitType: string;
  competitors: number;
  rent: number;
  revenueMin: number;
  revenueMax: number;
}

interface ComparisonTableProps {
  sites: ComparisonSite[];
  maxSites?: number;
  className?: string;
}

/**
 * ComparisonTable - Side-by-side with arrows + verdict row
 *
 * Features:
 * - Side-by-side feature rows with comparison arrows
 * - Verdict row showing winner
 * - Max 3 sites (strict limit)
 */
export default function ComparisonTable({
  sites,
  maxSites = 3,
  className = '',
}: ComparisonTableProps) {
  // Limit to max sites
  const limitedSites = sites.slice(0, maxSites);

  if (limitedSites.length === 0) {
    return null;
  }

  // Find the site with highest score (winner)
  const winner = limitedSites.reduce((prev, current) =>
    current.score > prev.score ? current : prev
  );

  // Calculate comparison indicators
  const getComparison = (
    value: number,
    baseValue: number,
    higherIsBetter: boolean = true
  ): 'up' | 'down' | 'same' => {
    const diff = value - baseValue;
    if (Math.abs(diff) < 0.01 * baseValue) return 'same'; // Within 1%
    return (diff > 0) === higherIsBetter ? 'up' : 'down';
  };

  const ComparisonIcon = ({ comparison }: { comparison: 'up' | 'down' | 'same' }) => {
    if (comparison === 'up') {
      return <ArrowUpIcon className="w-4 h-4 text-opportunity-high" />;
    }
    if (comparison === 'down') {
      return <ArrowDownIcon className="w-4 h-4 text-opportunity-low" />;
    }
    return <MinusIcon className="w-4 h-4 text-neutral-400" />;
  };

  const baselineSite = limitedSites[0];

  return (
    <div className={`bg-white border border-gradient-100 rounded-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="grid grid-cols-4 gap-4 p-6 bg-gradient-50 border-b border-gradient-100">
        <div className="text-sm font-medium text-neutral-600">Feature</div>
        {limitedSites.map((site) => (
          <div key={site.id} className="text-center">
            <div className="font-semibold text-neutral-900 mb-2">{site.name}</div>
            <ScoreChip score={site.score} size="sm" />
          </div>
        ))}
      </div>

      {/* Comparison rows */}
      <div className="divide-y divide-neutral-200">
        {/* Population */}
        <div className="grid grid-cols-4 gap-4 p-4 hover:bg-gradient-50 transition-colors">
          <div className="text-sm font-medium text-neutral-700">Population (1km)</div>
          {limitedSites.map((site, idx) => {
            const comparison = idx === 0 ? 'same' : getComparison(site.population, baselineSite.population, true);
            return (
              <div key={site.id} className="text-center flex items-center justify-center gap-2">
                <span className="text-sm text-neutral-900">{site.population.toLocaleString('fi-FI')}</span>
                {idx > 0 && <ComparisonIcon comparison={comparison} />}
              </div>
            );
          })}
        </div>

        {/* Income */}
        <div className="grid grid-cols-4 gap-4 p-4 hover:bg-gradient-50 transition-colors">
          <div className="text-sm font-medium text-neutral-700">Median Income</div>
          {limitedSites.map((site, idx) => {
            const comparison = idx === 0 ? 'same' : getComparison(site.income, baselineSite.income, true);
            return (
              <div key={site.id} className="text-center flex items-center justify-center gap-2">
                <span className="text-sm text-neutral-900">{formatCurrency(site.income)}</span>
                {idx > 0 && <ComparisonIcon comparison={comparison} />}
              </div>
            );
          })}
        </div>

        {/* Transit */}
        <div className="grid grid-cols-4 gap-4 p-4 hover:bg-gradient-50 transition-colors">
          <div className="text-sm font-medium text-neutral-700">Transit Access</div>
          {limitedSites.map((site) => (
            <div key={site.id} className="text-center">
              <span className="text-sm text-neutral-900">{site.transitType}</span>
            </div>
          ))}
        </div>

        {/* Competition */}
        <div className="grid grid-cols-4 gap-4 p-4 hover:bg-gradient-50 transition-colors">
          <div className="text-sm font-medium text-neutral-700">Competitors (1km)</div>
          {limitedSites.map((site, idx) => {
            const comparison = idx === 0 ? 'same' : getComparison(site.competitors, baselineSite.competitors, false);
            return (
              <div key={site.id} className="text-center flex items-center justify-center gap-2">
                <span className="text-sm text-neutral-900">{site.competitors}</span>
                {idx > 0 && <ComparisonIcon comparison={comparison} />}
              </div>
            );
          })}
        </div>

        {/* Rent */}
        <div className="grid grid-cols-4 gap-4 p-4 hover:bg-gradient-50 transition-colors">
          <div className="text-sm font-medium text-neutral-700">Rent (€/m²/mo)</div>
          {limitedSites.map((site, idx) => {
            const comparison = idx === 0 ? 'same' : getComparison(site.rent, baselineSite.rent, false);
            return (
              <div key={site.id} className="text-center flex items-center justify-center gap-2">
                <span className="text-sm text-neutral-900">€{site.rent}</span>
                {idx > 0 && <ComparisonIcon comparison={comparison} />}
              </div>
            );
          })}
        </div>

        {/* Revenue */}
        <div className="grid grid-cols-4 gap-4 p-4 hover:bg-gradient-50 transition-colors">
          <div className="text-sm font-medium text-neutral-700">Predicted Revenue</div>
          {limitedSites.map((site) => (
            <div key={site.id} className="text-center">
              <div className="text-sm text-neutral-900">
                {formatCurrency(site.revenueMin)} – {formatCurrency(site.revenueMax)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Verdict row */}
      <div className="p-6 bg-gradient-50 border-t border-gradient-200">
        <div className="flex items-center gap-3">
          <CheckCircleIcon className="w-6 h-6 text-opportunity-high flex-shrink-0" />
          <div>
            <span className="font-semibold text-neutral-900">{winner.name} wins</span>
            <span className="text-neutral-700">
              {' '}
              by +{winner.score - Math.min(...limitedSites.filter(s => s.id !== winner.id).map(s => s.score))} score points;{' '}
              predicted revenue{' '}
              +{formatCurrency(winner.revenueMin - Math.min(...limitedSites.filter(s => s.id !== winner.id).map(s => s.revenueMin)))} –
              +{formatCurrency(winner.revenueMax - Math.min(...limitedSites.filter(s => s.id !== winner.id).map(s => s.revenueMax)))}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
