// API Response Types matching backend schemas

export type SearchType = 'discovery' | 'single_site' | 'comparison';

export type Concept = 'QSR' | 'FastCasual' | 'Coffee' | 'CasualDining' | 'FineDining';

export type Recommendation = 'strong' | 'moderate' | 'weak' | 'pass';

export interface UniversalSearchResponse {
  search_type: SearchType;
  city?: string;
  addresses?: string[];
  requires_concept: boolean;
}

export interface DataCoverage {
  demographics: number;
  competition: number;
  transit: number;
  overall: number;
}

export interface MethodInfo {
  scoring_method: 'heuristic' | 'agent_based';
  data_sources: string[];
  last_updated: string;
  confidence_basis: string;
}

export interface AreaOpportunity {
  area_id: string;
  area_name: string;
  score: number;
  latitude: number;
  longitude: number;
  predicted_revenue_low: number;
  predicted_revenue_high: number;
  estimated_rent_psqft?: number;
  available_properties_count: number;
  confidence: number;
  coverage: DataCoverage;
}

export interface HeatmapPoint {
  latitude: number;
  longitude: number;
  score: number;
  weight: number;
  confidence?: number;
}

export interface DiscoveryResponse {
  city: string;
  concept: string;
  heatmap_data: HeatmapPoint[];
  top_opportunities: AreaOpportunity[];
  total_areas_scored: number;
  method: MethodInfo;
}

export interface SiteFeatures {
  population_1km?: number;
  population_density?: number;
  median_income?: number;
  age_18_24_percent?: number;
  competitors_count?: number;
  competitors_per_1k_residents?: number;
  nearest_metro_distance_m?: number;
  nearest_tram_distance_m?: number;
  walkability_score?: number;
  population_score?: number;
  income_score?: number;
  access_score?: number;
  competition_score?: number;
  walkability_score_component?: number;
}

export interface SitePrediction {
  address: string;
  latitude: number;
  longitude: number;
  postal_code?: string;
  score: number;
  predicted_revenue_low: number;
  predicted_revenue_mid: number;
  predicted_revenue_high: number;
  confidence: number;
  coverage: DataCoverage;
  rank?: number;
  recommendation: Recommendation;
  suggested_offer_psqft?: number;
  expected_roi_months?: number;
  strengths: string[];
  risks: string[];
  features: SiteFeatures;
}

export interface SiteAnalysisResponse {
  concept: string;
  sites: SitePrediction[];
  ranking?: number[];
  cannibalization_warning?: string;
  prediction_id: string;
  method: MethodInfo;
}

export interface OutcomeSubmission {
  prediction_id: string;
  actual_revenue: number;
  opening_date: string;
  notes?: string;
}

export interface AccuracyStats {
  total_predictions: number;
  sites_opened: number;
  within_predicted_band: number;
  accuracy_rate: number;
  avg_variance_percent: number;
}

// UI Helper Types

export interface ConceptOption {
  value: Concept;
  label: string;
  description: string;
}

export const CONCEPT_OPTIONS: ConceptOption[] = [
  { value: 'QSR', label: 'QSR', description: 'Quick Service Restaurant' },
  { value: 'FastCasual', label: 'Fast Casual', description: 'Fast Casual Dining' },
  { value: 'Coffee', label: 'Coffee', description: 'Coffee Shop' },
  { value: 'CasualDining', label: 'Casual Dining', description: 'Casual Dining Restaurant' },
  { value: 'FineDining', label: 'Fine Dining', description: 'Fine Dining Restaurant' },
];

export function getScoreColor(score: number): string {
  if (score >= 85) return 'text-opportunity-high';
  if (score >= 70) return 'text-opportunity-medium';
  return 'text-opportunity-low';
}

export function getScoreBgColor(score: number): string {
  if (score >= 85) return 'bg-opportunity-high';
  if (score >= 70) return 'bg-opportunity-medium';
  return 'bg-opportunity-low';
}

export function getRecommendationLabel(recommendation: Recommendation): string {
  const labels = {
    strong: 'Strong Location',
    moderate: 'Moderate Opportunity',
    weak: 'Weak Potential',
    pass: 'Pass'
  };
  return labels[recommendation];
}

export function formatCurrency(amount: number, currency: string = 'EUR'): string {
  return new Intl.NumberFormat('en-FI', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-FI').format(num);
}
