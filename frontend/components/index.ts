/**
 * Spotlight Component Library
 * Export all components for easy importing
 */

// Trust Components
export { default as ConfidenceBadge } from './trust/ConfidenceBadge';
export { default as DataCoverageBar } from './trust/DataCoverageBar';
export { default as MethodModal } from './trust/MethodModal';
export { default as ScoreChip } from './trust/ScoreChip';

// Core UI Components
export { default as HeatMap } from './core/HeatMap';
export { default as InsightList } from './core/InsightList';
export { default as MetricHero } from './core/MetricHero';
export { default as OpportunityCard } from './core/OpportunityCard';
export { default as UniversalSearch } from './UniversalSearch';

// UX Components
export { default as ComparisonTable } from './ux/ComparisonTable';
export { default as SkeletonCard } from './ux/SkeletonCard';
export { default as StickyActionBar } from './ux/StickyActionBar';
export { default as ToggleGroup } from './ux/ToggleGroup';

// UI Components
export { default as Button } from './ui/Button';

// Type exports
export type { Insight } from './core/InsightList';
export type { ComparisonSite } from './ux/ComparisonTable';
export type { Toggle } from './ux/ToggleGroup';
