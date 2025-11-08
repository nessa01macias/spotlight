'use client';

import { useState } from 'react';
import MetricHero from '@/components/core/MetricHero';
import OpportunityCard from '@/components/core/OpportunityCard';
import InsightList, { Insight } from '@/components/core/InsightList';
import ConfidenceBadge from '@/components/trust/ConfidenceBadge';
import DataCoverageBar from '@/components/trust/DataCoverageBar';
import MethodModal from '@/components/trust/MethodModal';
import ScoreChip from '@/components/trust/ScoreChip';
import StickyActionBar from '@/components/ux/StickyActionBar';
import SkeletonCard from '@/components/ux/SkeletonCard';
import ToggleGroup, { Toggle } from '@/components/ux/ToggleGroup';
import ComparisonTable, { ComparisonSite } from '@/components/ux/ComparisonTable';
import Button from '@/components/ui/Button';
import { grainTexture } from '@/lib/design-system';

/**
 * Demo Page - Showcases all components with realistic data
 *
 * This page demonstrates the complete Spotlight UI redesign:
 * - Trust components (ConfidenceBadge, DataCoverageBar, MethodModal, ScoreChip)
 * - Core components (MetricHero, OpportunityCard, InsightList)
 * - UX components (StickyActionBar, SkeletonCard, ToggleGroup, ComparisonTable)
 */
export default function DemoPage() {
  const [showMethodModal, setShowMethodModal] = useState(false);
  const [showLoading, setShowLoading] = useState(false);

  // Sample insights data
  const insights: Insight[] = [
    {
      type: 'strength',
      text: '28,000 people within 1km walking distance; median income €48,000 (+6% vs target demographic)',
    },
    {
      type: 'strength',
      text: 'Metro hub with 50,000+ daily foot traffic; 3 universities within 500m driving student demand',
    },
    {
      type: 'risk',
      text: '12 competitors nearby (0.43 per 1,000 people); manageable density but requires differentiation',
    },
    {
      type: 'risk',
      text: 'Limited parking access; 85% of traffic is pedestrian/transit-based',
    },
    {
      type: 'recommendation',
      text: 'Focus on quick-service format (7-12 min avg visit) to capture high foot traffic',
    },
    {
      type: 'recommendation',
      text: 'Consider student-friendly pricing; €8-12 average ticket optimizes volume + margin',
    },
  ];

  // Sample comparison sites
  const comparisonSites: ComparisonSite[] = [
    {
      id: '1',
      name: 'Kamppi - University District',
      score: 91,
      population: 28000,
      income: 48000,
      transitType: 'Metro',
      competitors: 12,
      rent: 42,
      revenueMin: 1600000,
      revenueMax: 1900000,
    },
    {
      id: '2',
      name: 'Kallio - Residential',
      score: 87,
      population: 22000,
      income: 46000,
      transitType: 'Tram',
      competitors: 18,
      rent: 38,
      revenueMin: 1400000,
      revenueMax: 1700000,
    },
    {
      id: '3',
      name: 'Pasila - Business District',
      score: 84,
      population: 19000,
      income: 52000,
      transitType: 'Train',
      competitors: 9,
      rent: 45,
      revenueMin: 1300000,
      revenueMax: 1500000,
    },
  ];

  // Sample toggles
  const toggles: Toggle[] = [
    {
      id: 'safety-proxy',
      label: 'Safety proxy',
      description: 'Uses nightlife density + public stats (low weight, optional)',
      defaultValue: true,
      tooltip: 'Safety proxy uses nightlife density + public offense stats. Max 5% weight cap, correlation only.',
    },
    {
      id: 'radius',
      label: 'Use radius instead of drive-time',
      description: 'Calculate catchment area by straight-line distance',
      defaultValue: false,
    },
  ];

  return (
    <div
      className="min-h-screen bg-gradient-to-br from-gradient-50 via-white to-gradient-100 pb-24"
      style={grainTexture}
    >
      {/* Header */}
      <div className="bg-white border-b border-gradient-100">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-semibold text-neutral-900">Spotlight UI Demo</h1>
              <p className="text-neutral-600 mt-1">Complete component showcase</p>
            </div>
            <a href="/" className="text-gradient-400 hover:underline">
              ← Back to Home
            </a>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 py-12 space-y-16">
        {/* Section 1: Trust Components */}
        <section>
          <h2 className="text-2xl font-semibold text-neutral-900 mb-8">Trust Components</h2>

          <div className="space-y-8">
            {/* MetricHero */}
            <div>
              <h3 className="text-lg font-medium text-neutral-700 mb-4">MetricHero with ConfidenceBadge</h3>
              <MetricHero
                score={91}
                revenueMin={1600000}
                revenueMax={1900000}
                confidence={0.82}
                title="Kamppi - University District"
                subtitle="Helsinki, Finland"
                onMethodClick={() => setShowMethodModal(true)}
              />
            </div>

            {/* Individual Trust Components */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-medium text-neutral-700 mb-4">Confidence Badges</h3>
                <div className="bg-white border border-gradient-100 rounded-lg p-6 space-y-4">
                  <ConfidenceBadge confidence={0.95} onModalClick={() => setShowMethodModal(true)} />
                  <ConfidenceBadge confidence={0.78} onModalClick={() => setShowMethodModal(true)} />
                  <ConfidenceBadge confidence={0.55} onModalClick={() => setShowMethodModal(true)} />
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium text-neutral-700 mb-4">Score Chips</h3>
                <div className="bg-white border border-gradient-100 rounded-lg p-6 space-y-4">
                  <div className="flex items-center gap-3">
                    <ScoreChip score={91} size="sm" />
                    <ScoreChip score={91} size="md" />
                    <ScoreChip score={91} size="lg" />
                  </div>
                  <div className="flex items-center gap-3">
                    <ScoreChip score={72} size="md" />
                    <ScoreChip score={45} size="md" />
                  </div>
                </div>
              </div>
            </div>

            {/* Data Coverage Bar */}
            <div>
              <h3 className="text-lg font-medium text-neutral-700 mb-4">Data Coverage Bar</h3>
              <div className="bg-white border border-gradient-100 rounded-lg p-6">
                <DataCoverageBar />
              </div>
            </div>
          </div>
        </section>

        {/* Section 2: Core UI Components */}
        <section>
          <h2 className="text-2xl font-semibold text-neutral-900 mb-8">Core UI Components</h2>

          <div className="space-y-8">
            {/* Opportunity Cards */}
            <div>
              <h3 className="text-lg font-medium text-neutral-700 mb-4">Opportunity Cards</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <OpportunityCard
                  name="Kamppi - University District"
                  score={91}
                  revenueMin={1600000}
                  revenueMax={1900000}
                  confidence={0.82}
                  onView={() => alert('View clicked')}
                  onCompare={() => alert('Compare clicked')}
                />
                <OpportunityCard
                  name="Kallio - Residential"
                  score={87}
                  revenueMin={1400000}
                  revenueMax={1700000}
                  confidence={0.75}
                  onView={() => alert('View clicked')}
                />
              </div>
            </div>

            {/* Insight List */}
            <div>
              <h3 className="text-lg font-medium text-neutral-700 mb-4">Insight List (with inline math)</h3>
              <div className="bg-white border border-gradient-100 rounded-lg p-6">
                <div className="space-y-8">
                  <InsightList
                    title="Strengths"
                    insights={insights.filter(i => i.type === 'strength')}
                  />
                  <InsightList
                    title="Risks"
                    insights={insights.filter(i => i.type === 'risk')}
                  />
                  <InsightList
                    title="Recommendations"
                    insights={insights.filter(i => i.type === 'recommendation')}
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Section 3: UX Components */}
        <section>
          <h2 className="text-2xl font-semibold text-neutral-900 mb-8">UX Components</h2>

          <div className="space-y-8">
            {/* Toggle Group */}
            <div>
              <h3 className="text-lg font-medium text-neutral-700 mb-4">Toggle Group (Filters)</h3>
              <ToggleGroup
                title="Analysis Options"
                toggles={toggles}
                onChange={(id, value) => console.log(`${id}: ${value}`)}
              />
            </div>

            {/* Comparison Table */}
            <div>
              <h3 className="text-lg font-medium text-neutral-700 mb-4">Comparison Table (Max 3 sites)</h3>
              <ComparisonTable sites={comparisonSites} />
            </div>

            {/* Loading States */}
            <div>
              <h3 className="text-lg font-medium text-neutral-700 mb-4">Loading States (Skeletons)</h3>
              <div className="space-y-6">
                <div>
                  <p className="text-sm text-neutral-600 mb-3">Hero Skeleton</p>
                  <SkeletonCard variant="hero" />
                </div>
                <div>
                  <p className="text-sm text-neutral-600 mb-3">Card Skeletons</p>
                  <SkeletonCard variant="card" count={2} />
                </div>
                <div>
                  <p className="text-sm text-neutral-600 mb-3">List Skeletons</p>
                  <div className="bg-white border border-gradient-100 rounded-lg p-6">
                    <SkeletonCard variant="list" count={3} />
                  </div>
                </div>
              </div>
            </div>

            {/* Buttons */}
            <div>
              <h3 className="text-lg font-medium text-neutral-700 mb-4">Buttons</h3>
              <div className="bg-white border border-gradient-100 rounded-lg p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <Button variant="primary" size="sm">Primary Small</Button>
                  <Button variant="primary" size="md">Primary Medium</Button>
                  <Button variant="primary" size="lg">Primary Large</Button>
                </div>
                <div className="flex items-center gap-3">
                  <Button variant="secondary" size="md">Secondary</Button>
                  <Button variant="tertiary" size="md">Tertiary</Button>
                </div>
                <div className="flex items-center gap-3">
                  <Button variant="primary" size="md" isLoading>Loading...</Button>
                  <Button variant="primary" size="md" disabled>Disabled</Button>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Section 4: Interactive Demo */}
        <section className="bg-gradient-50 border border-gradient-100 rounded-2xl p-8">
          <h2 className="text-2xl font-semibold text-neutral-900 mb-4">Interactive Demo</h2>
          <p className="text-neutral-600 mb-6">
            Toggle loading states and open modals to see components in action.
          </p>

          <div className="flex items-center gap-3">
            <Button
              variant="primary"
              onClick={() => setShowLoading(!showLoading)}
            >
              {showLoading ? 'Hide Loading States' : 'Show Loading States'}
            </Button>
            <Button
              variant="secondary"
              onClick={() => setShowMethodModal(true)}
            >
              Open Method Modal
            </Button>
          </div>

          {showLoading && (
            <div className="mt-6">
              <SkeletonCard variant="hero" />
            </div>
          )}
        </section>
      </div>

      {/* Sticky Action Bar */}
      <StickyActionBar
        onCompare={() => alert('Compare clicked!')}
        onDownload={() => alert('Download clicked!')}
      />

      {/* Method Modal */}
      <MethodModal
        isOpen={showMethodModal}
        onClose={() => setShowMethodModal(false)}
      />
    </div>
  );
}
