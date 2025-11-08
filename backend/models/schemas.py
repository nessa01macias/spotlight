from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============= Search Schemas =============

class UniversalSearchRequest(BaseModel):
    """Universal search input - handles city, address, or multiple addresses"""
    query: str = Field(..., description="City, address, or multiple addresses")
    concept: Optional[str] = None  # Asked after if needed


class UniversalSearchResponse(BaseModel):
    """Response from universal search with routing info"""
    search_type: Literal["discovery", "single_site", "comparison"]
    city: Optional[str] = None
    addresses: Optional[List[str]] = None
    requires_concept: bool = False


# ============= Trust Layer Schemas =============

class DataCoverage(BaseModel):
    """Data coverage metrics for transparency"""
    demographics: float = Field(..., ge=0, le=1, description="0-1 score for demographic data quality")
    competition: float = Field(..., ge=0, le=1, description="0-1 score for competition data quality")
    transit: float = Field(..., ge=0, le=1, description="0-1 score for transit data quality")
    overall: float = Field(..., ge=0, le=1, description="Overall data coverage score")


class MethodInfo(BaseModel):
    """Method transparency - how prediction was made"""
    scoring_method: Literal["heuristic", "agent_based"]
    data_sources: List[str]
    last_updated: str  # ISO timestamp
    confidence_basis: str  # Brief explanation


# ============= Discovery Schemas =============

class DiscoveryRequest(BaseModel):
    """Request for city-wide discovery view"""
    city: str
    concept: str = Field(..., description="QSR, FastCasual, Coffee, etc.")


class AreaOpportunity(BaseModel):
    """Individual area in discovery view"""
    area_id: str
    area_name: str
    score: float = Field(..., ge=0, le=100)
    latitude: float
    longitude: float
    predicted_revenue_low: float
    predicted_revenue_high: float
    estimated_rent_psqft: Optional[float] = None
    available_properties_count: int = 0
    
    # Trust layer
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence 0-1")
    coverage: DataCoverage


class DiscoveryResponse(BaseModel):
    """Response for discovery view - heatmap + top areas"""
    city: str
    concept: str
    heatmap_data: List[Dict[str, Any]]  # Grid points with scores
    top_opportunities: List[AreaOpportunity]
    total_areas_scored: int
    
    # Trust layer
    method: MethodInfo


# ============= Site Analysis Schemas =============

class SiteAnalysisRequest(BaseModel):
    """Request for analyzing one or more sites"""
    addresses: List[str] = Field(..., min_items=1, max_items=10)
    concept: str


class SiteFeatures(BaseModel):
    """Detailed features for a site"""
    # Demographics
    population_1km: Optional[int] = None
    population_density: Optional[float] = None
    median_income: Optional[float] = None
    age_18_24_percent: Optional[float] = None

    # Competition
    competitors_count: Optional[int] = None
    competitors_per_1k_residents: Optional[float] = None
    competition_saturation: Optional[float] = None

    # Traffic & Access
    nearest_metro_distance_m: Optional[float] = None
    nearest_tram_distance_m: Optional[float] = None
    walkability_score: Optional[float] = None
    daily_traffic_estimate: Optional[int] = None

    # Score components
    population_score: Optional[float] = None
    income_score: Optional[float] = None
    access_score: Optional[float] = None
    competition_score: Optional[float] = None
    walkability_score_component: Optional[float] = None


class SitePrediction(BaseModel):
    """Prediction for a single site"""
    address: str
    latitude: float
    longitude: float
    postal_code: Optional[str] = None

    # Core prediction
    score: float = Field(..., ge=0, le=100)
    predicted_revenue_low: float
    predicted_revenue_mid: float
    predicted_revenue_high: float
    
    # Trust layer
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence 0-1")
    coverage: DataCoverage

    # Ranking (if comparison)
    rank: Optional[int] = None

    # Recommendation
    recommendation: Literal["strong", "moderate", "weak", "pass"]
    suggested_offer_psqft: Optional[float] = None
    expected_roi_months: Optional[int] = None

    # Insights
    strengths: List[str]
    risks: List[str]

    # Detailed features
    features: SiteFeatures

    # NEW: Agno reasoning traces (for transparency)
    reasoning_summary: Optional[str] = None
    agent_reasoning: Optional[Dict[str, Any]] = None


class SiteAnalysisResponse(BaseModel):
    """Response for site analysis"""
    concept: str
    sites: List[SitePrediction]
    ranking: Optional[List[int]] = None  # Indices in order best→worst
    cannibalization_warning: Optional[str] = None
    prediction_id: str  # For outcome tracking
    
    # Trust layer
    method: MethodInfo


# ============= Area Detail Schemas =============

class AvailableProperty(BaseModel):
    """Property listing in an area"""
    address: str
    size_sqft: float
    rent_psqft: float
    total_rent_monthly: float
    latitude: float
    longitude: float
    listing_url: Optional[str] = None


class AreaDetailRequest(BaseModel):
    """Request for area detail page"""
    area_id: str
    concept: str


class AreaDetailResponse(BaseModel):
    """Detailed area information"""
    area_id: str
    area_name: str
    city: str
    score: float
    predicted_revenue_low: float
    predicted_revenue_mid: float
    predicted_revenue_high: float
    
    # Trust layer
    confidence: float = Field(..., ge=0, le=1)
    coverage: DataCoverage
    method: MethodInfo

    # Available properties
    available_properties: List[AvailableProperty]

    # Why this area works
    why: List[str] = Field(..., description="Brief bullet points explaining the score")
    demographics: Dict[str, Any]
    competition_analysis: Dict[str, Any]
    traffic_access: Dict[str, Any]
    
    # Coordinates
    latitude: float
    longitude: float

    # Insights
    strengths: List[str]
    risks: List[str]

    # Actions
    nearby_alternatives: List[AreaOpportunity]


# ============= Outcome Tracking Schemas =============

class OutcomeSubmission(BaseModel):
    """Submit actual results after opening"""
    prediction_id: str
    actual_revenue: float
    opening_date: datetime
    notes: Optional[str] = None


class OutcomeResponse(BaseModel):
    """Response after submitting outcome"""
    status: str
    variance_percent: float
    within_predicted_band: bool
    message: str


class AccuracyStats(BaseModel):
    """Model accuracy statistics"""
    total_predictions: int
    sites_opened: int
    within_predicted_band: int
    accuracy_rate: float
    avg_variance_percent: float


# ============= Report Schemas =============

class ReportRequest(BaseModel):
    """Request for PDF report generation"""
    prediction_id: Optional[str] = None
    area_id: Optional[str] = None
    concept: str
    include_map: bool = True


class ReportResponse(BaseModel):
    """Response with PDF download link"""
    pdf_url: str
    report_id: str
    generated_at: datetime


# ============= Recommend Schemas (NEW - Address-first flow) =============

class RecommendRequest(BaseModel):
    """Request for address recommendations"""
    city: str = Field(..., description="City to search in (e.g., 'Helsinki')")
    concept: str = Field(..., description="Restaurant concept (QSR, FastCasual, Coffee, etc.)")
    limit: int = Field(10, ge=1, le=20, description="Number of addresses to return")
    include_crime: bool = Field(False, description="Include crime penalty in scoring (capped at 5%)")


class MetricProvenance(BaseModel):
    """Provenance information for a single metric"""
    score: float = Field(..., description="Score contribution (0-100)")
    weight: float = Field(..., description="Weight in overall score (0-1)")
    weighted_score: float = Field(..., description="score * weight")
    source: str = Field(..., description="Data source name (e.g., 'Statistics Finland')")
    coverage: float = Field(..., ge=0, le=1, description="Data coverage quality (0-1)")
    raw_value: Optional[Any] = None  # Original data (e.g., 27000 for population)
    raw_unit: Optional[str] = None  # Unit for raw_value (e.g., "people", "meters")


class ScoreProvenance(BaseModel):
    """Complete provenance breakdown for transparency"""
    population: MetricProvenance
    income_fit: MetricProvenance
    transit_access: MetricProvenance
    competition_inverse: MetricProvenance
    traffic_access: MetricProvenance
    crime_penalty_cap: Optional[MetricProvenance] = None
    total_score: float = Field(..., description="Sum of all weighted scores")
    confidence_basis: str = Field(..., description="Explanation of confidence calculation")


class RecommendedAddress(BaseModel):
    """Single recommended address with full scoring"""
    rank: int
    address: str
    lat: float
    lng: float
    score: float = Field(..., ge=0, le=100)
    revenue_min_eur: int
    revenue_max_eur: int
    confidence: float = Field(..., ge=0, le=1)
    coverage: Dict[str, float]  # {demo, comp, access, traffic, rent, crime}
    why: List[str] = Field(..., description="Numeric reason bullets (e.g., 'Pop 27k/800m')")
    decision: Literal["MAKE_OFFER", "NEGOTIATE", "PASS"]
    decision_reasoning: Optional[str] = Field(None, description="Explanation of why this decision was made")
    area_id: Optional[str] = None
    nearby_property_search_url: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    provenance: Optional[ScoreProvenance] = None  # NEW: Detailed provenance breakdown


class WeightsInfo(BaseModel):
    """Scoring weights for transparency"""
    weights_version: str
    weights: Dict[str, float]
    sources: List[Dict[str, str]]  # [{name, refreshed_at}]


class RecommendResponse(BaseModel):
    """Response with top N recommended addresses"""
    job_id: str
    city: str
    concept: str
    top: List[RecommendedAddress]
    method: WeightsInfo
    degraded: List[str] = Field(default_factory=list, description="Warnings (e.g., 'OVERPASS_CACHED')")


class JobStatusResponse(BaseModel):
    """Job status for SSE or polling"""
    job_id: str
    status: Literal["pending", "running", "complete", "failed", "degraded"]
    result: Optional[RecommendResponse] = None
    error: Optional[str] = None


# ============= Pursue Action Schemas (NEW - Execution actions) =============

class PursueRequest(BaseModel):
    """Request to pursue an address (generate broker email)"""
    address: str
    lat: float
    lng: float
    concept: str
    score: float
    revenue_min_eur: int
    revenue_max_eur: int
    why: List[str]


class PursueResponse(BaseModel):
    """Response with mailto link and Gmail URL"""
    mailto_link: str
    gmail_url: str
    subject: str
    body: str
