"""
Spotlight - Restaurant Site Selection API
Main FastAPI application with smart routing
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import re
import os
from dotenv import load_dotenv

from models.schemas import (
    UniversalSearchRequest,
    UniversalSearchResponse,
    DiscoveryRequest,
    DiscoveryResponse,
    AreaOpportunity,
    SiteAnalysisRequest,
    SiteAnalysisResponse,
    SitePrediction,
    SiteFeatures,
    OutcomeSubmission,
    OutcomeResponse,
    AccuracyStats
)
from models.db_init import init_db, get_db
from agents.data_collector import DataCollector
from agents.scorer import ScoringEngine
# from agents.agno.orchestrator import OrchestratorAgent  # Phase 2 - Agno agents
from services.digitransit import DigitransitService
from services.trust_metrics import TrustMetrics

# NEW: Import routers
from routes.recommend import router as recommend_router
from routes.concepts import router as concepts_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Spotlight API",
    description="Evidence-based site selection for Finland",
    version="2.0.0"  # Bumped for new recommend flow
)

# Include routers
app.include_router(recommend_router)
app.include_router(concepts_router)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Spotlight API...")
    init_db()
    print("✓ Database initialized")

# CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3002").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_collector = DataCollector()
scorer = ScoringEngine()  # Legacy scorer for /api/discover
# orchestrator = OrchestratorAgent()  # Phase 2: Agno orchestrator for /api/analyze
geocoding_service = DigitransitService()


# ============= Health Check =============

@app.get("/")
async def root():
    return {
        "app": "ExpansionAI",
        "status": "operational",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ============= Smart Routing =============

@app.post("/api/search", response_model=UniversalSearchResponse)
async def universal_search(request: UniversalSearchRequest):
    """
    Universal search - detects input type and routes appropriately

    Input types:
    - City name: "Helsinki" → discovery
    - Single address: "Mannerheimintie 20, Helsinki" → single_site
    - Multiple addresses: "addr1, addr2, addr3" → comparison
    """
    query = request.query.strip()

    # Detect input type
    search_type = _detect_search_type(query)

    if search_type == "city":
        return UniversalSearchResponse(
            search_type="discovery",
            city=query,
            requires_concept=True if not request.concept else False
        )
    elif search_type == "postal_code":
        # For postal code, return as discovery (will be handled by /api/discover)
        return UniversalSearchResponse(
            search_type="discovery",
            city=query,  # Pass postal code as "city"
            requires_concept=True if not request.concept else False
        )
    elif search_type == "single_address":
        return UniversalSearchResponse(
            search_type="single_site",
            addresses=[query],
            requires_concept=True if not request.concept else False
        )
    elif search_type == "multiple_addresses":
        addresses = _extract_addresses(query)
        return UniversalSearchResponse(
            search_type="comparison",
            addresses=addresses,
            requires_concept=True if not request.concept else False
        )
    else:
        raise HTTPException(status_code=400, detail="Could not parse search query")


def _detect_search_type(query: str) -> str:
    """Detect whether query is city, single address, postal code, or multiple addresses"""

    # Check for multiple addresses (separated by newlines or semicolons)
    if "\n" in query or ";" in query:
        return "multiple_addresses"

    # Check if it's a Finnish postal code (5 digits, possibly with leading zero)
    if re.match(r'^\d{5}$', query.strip()):
        return "postal_code"

    # Check if it's just a city name (no numbers, short)
    if len(query.split()) <= 2 and not re.search(r'\d', query):
        return "city"

    # Check if it contains address-like patterns (numbers + street)
    if re.search(r'\d+\s+[A-Za-zäöåÄÖÅ]+', query):
        return "single_address"

    # Default to city
    return "city"


def _extract_addresses(query: str) -> List[str]:
    """Extract multiple addresses from query"""
    # Split by newline or semicolon
    if "\n" in query:
        addresses = [addr.strip() for addr in query.split("\n") if addr.strip()]
    elif ";" in query:
        addresses = [addr.strip() for addr in query.split(";") if addr.strip()]
    else:
        addresses = [query.strip()]

    return addresses


# ============= Discovery Endpoint =============

async def _analyze_postal_area(postal_code: str, concept: str) -> DiscoveryResponse:
    """
    Analyze a specific postal code area
    Returns discovery-style response for single postal area
    """
    # Fetch demographics for this postal code
    demographics = await data_collector.statfin.get_demographics_by_postal_code(postal_code)
    
    if not demographics:
        raise HTTPException(
            status_code=404, 
            detail=f"Postal code {postal_code} not found in Finland. Please check the postal code."
        )
    
    area_name = demographics.get("area_name", postal_code)
    
    # Get coordinates from PAAVO (already converted to WGS84)
    lat = demographics.get("latitude")
    lng = demographics.get("longitude")
    
    if not lat or not lng:
        raise HTTPException(
            status_code=400,
            detail=f"No geographic coordinates available for postal code {postal_code}"
        )
    
    # Collect location-based data (competition, transit, etc.)
    features = await data_collector.collect_area_data(area_name, lat, lng, concept)
    
    # Merge in demographics from PAAVO
    features.update({
        "postal_code": postal_code,
        "median_income": demographics.get("median_income"),
        "mean_income": demographics.get("mean_income"),
        "age_0_14_percent": demographics.get("age_0_14_percent"),
        "age_15_64_percent": demographics.get("age_15_64_percent"),
        "age_65_plus_percent": demographics.get("age_65_plus_percent"),
        "higher_education_percent": demographics.get("higher_education_percent"),
        "employment_rate": demographics.get("employment_rate"),
        "average_age": demographics.get("average_age"),
    })
    
    # Calculate score
    score_result = scorer.calculate_score(features, concept)
    
    # Calculate trust metrics
    coverage = TrustMetrics.calculate_coverage(features)
    confidence = TrustMetrics.calculate_confidence(
        score_components=score_result["score_components"],
        coverage=coverage
    )
    
    # Create single opportunity
    opportunity = AreaOpportunity(
        area_id=f"postal_{postal_code}",
        area_name=f"{area_name} ({postal_code})",
        score=score_result["score"],
        latitude=lat,
        longitude=lng,
        predicted_revenue_low=score_result["revenue_low"],
        predicted_revenue_high=score_result["revenue_high"],
        estimated_rent_psqft=0,  # Unknown for postal code search
        available_properties_count=0,
        confidence=confidence,
        coverage=coverage
    )
    
    # Create heatmap with single point
    heatmap_data = [{
        "latitude": lat,
        "longitude": lng,
        "score": score_result["score"],
        "weight": score_result["score"] / 100,
        "confidence": confidence
    }]
    
    # Generate method info
    method_info = TrustMetrics.get_method_info(
        scoring_method="heuristic",
        features_used=features
    )
    
    return DiscoveryResponse(
        city=f"{area_name} ({postal_code})",
        concept=concept,
        heatmap_data=heatmap_data,
        top_opportunities=[opportunity],
        total_areas_scored=1,
        method=method_info
    )


@app.post("/api/discover", response_model=DiscoveryResponse)
async def discover_opportunities(request: DiscoveryRequest):
    """
    City-wide discovery view with heatmap + top opportunities
    NOW SUPPORTS ALL FINNISH CITIES!
    """
    # Check if it's a postal code (5 digits)
    if re.match(r'^\d{5}$', request.city.strip()):
        # Handle postal code analysis
        return await _analyze_postal_area(request.city, request.concept)

    # Check if city is supported
    city_lower = request.city.lower()
    
    # Get pre-defined areas for supported cities
    if city_lower in ["helsinki", "espoo", "vantaa"]:
        # Use pre-defined areas for Helsinki metro
        helsinki_areas = _get_helsinki_areas()
    else:
        # For other Finnish cities, generate areas dynamically
        # This will be implemented in Phase 2 with grid-based discovery
        raise HTTPException(
            status_code=501,
            detail=f"City-wide discovery for '{request.city}' coming soon! For now, try:\n"
                   f"1. Enter a specific address in {request.city}\n"
                   f"2. Enter a postal code (e.g., 33100 for Tampere center)\n"
                   f"3. Use Helsinki, Espoo, or Vantaa for full city discovery"
        )

    # Score each area for the concept
    scored_areas = []
    for area in helsinki_areas:
        try:
            # Collect data for area
            features = await data_collector.collect_area_data(
                area["name"],
                area["lat"],
                area["lng"],
                request.concept
            )

            # Calculate score
            score_result = scorer.calculate_score(features, request.concept)
            
            # Calculate trust metrics
            coverage = TrustMetrics.calculate_coverage(features)
            confidence = TrustMetrics.calculate_confidence(
                score_components=score_result["score_components"],
                coverage=coverage
            )

            scored_areas.append({
                "area_id": f"helsinki_{area['id']}",
                "area_name": area["name"],
                "score": score_result["score"],
                "latitude": area["lat"],
                "longitude": area["lng"],
                "predicted_revenue_low": score_result["revenue_low"],
                "predicted_revenue_high": score_result["revenue_high"],
                "estimated_rent_psqft": area.get("rent_psqft", 40),
                "available_properties_count": area.get("properties_count", 0),
                "confidence": confidence,
                "coverage": coverage
            })
        except Exception as e:
            print(f"Error scoring area {area['name']}: {e}")
            continue

    # Sort by score
    scored_areas.sort(key=lambda x: x["score"], reverse=True)

    # Top opportunities (top 10)
    top_opportunities = [
        AreaOpportunity(**area) for area in scored_areas[:10]
    ]

    # Heatmap data (all scored areas)
    heatmap_data = [
        {
            "latitude": area["latitude"],
            "longitude": area["longitude"],
            "score": area["score"],
            "weight": area["score"] / 100,  # Normalize for heatmap
            "confidence": area["confidence"]
        }
        for area in scored_areas
    ]
    
    # Generate method info
    method_info = TrustMetrics.get_method_info(
        scoring_method="heuristic",
        features_used=scored_areas[0] if scored_areas else {}
    )

    return DiscoveryResponse(
        city=request.city,
        concept=request.concept,
        heatmap_data=heatmap_data,
        top_opportunities=top_opportunities,
        total_areas_scored=len(scored_areas),
        method=method_info
    )


def _get_helsinki_areas() -> List[Dict[str, Any]]:
    """
    Pre-defined Helsinki areas for MVP
    In production, generate grid dynamically
    """
    return [
        {"id": "kamppi", "name": "Kamppi", "lat": 60.1699, "lng": 24.9342, "rent_psqft": 42, "properties_count": 3},
        {"id": "kallio", "name": "Kallio", "lat": 60.1847, "lng": 24.9504, "rent_psqft": 35, "properties_count": 2},
        {"id": "pasila", "name": "Pasila", "lat": 60.1989, "lng": 24.9339, "rent_psqft": 38, "properties_count": 1},
        {"id": "toolo", "name": "Töölö", "lat": 60.1777, "lng": 24.9157, "rent_psqft": 44, "properties_count": 2},
        {"id": "punavuori", "name": "Punavuori", "lat": 60.1585, "lng": 24.9398, "rent_psqft": 48, "properties_count": 4},
        {"id": "kruununhaka", "name": "Kruununhaka", "lat": 60.1729, "lng": 24.9560, "rent_psqft": 40, "properties_count": 1},
        {"id": "ullanlinna", "name": "Ullanlinna", "lat": 60.1586, "lng": 24.9519, "rent_psqft": 46, "properties_count": 3},
        {"id": "eira", "name": "Eira", "lat": 60.1543, "lng": 24.9374, "rent_psqft": 52, "properties_count": 2},
    ]


# ============= Area Detail Endpoint =============

@app.get("/api/area/{area_id}")
async def get_area_detail(
    area_id: str,
    concept: str
):
    """
    Get detailed information about a specific area
    This is what users see when they click a heatmap tile
    """
    # Parse area_id (format: "helsinki_kamppi" or "postal_00100")
    if area_id.startswith("postal_"):
        # Postal code area
        postal_code = area_id.replace("postal_", "")
        demographics = await data_collector.statfin.get_demographics_by_postal_code(postal_code)
        
        if not demographics:
            raise HTTPException(status_code=404, detail=f"Postal code {postal_code} not found")
        
        area_name = demographics.get("area_name", postal_code)
        city = "Finland"  # Generic for postal codes
        lat = demographics.get("latitude")
        lng = demographics.get("longitude")
        
        # Collect full data
        features = await data_collector.collect_area_data(area_name, lat, lng, concept)
        features.update({
            "postal_code": postal_code,
            "median_income": demographics.get("median_income"),
            "mean_income": demographics.get("mean_income"),
            "higher_education_percent": demographics.get("higher_education_percent"),
        })
        
    elif area_id.startswith("helsinki_"):
        # Pre-defined Helsinki area
        area_key = area_id.replace("helsinki_", "")
        helsinki_areas = _get_helsinki_areas()
        area_data = next((a for a in helsinki_areas if a["id"] == area_key), None)
        
        if not area_data:
            raise HTTPException(status_code=404, detail=f"Area {area_id} not found")
        
        area_name = area_data["name"]
        city = "Helsinki"
        lat = area_data["lat"]
        lng = area_data["lng"]
        
        # Collect data
        features = await data_collector.collect_area_data(area_name, lat, lng, concept)
    else:
        raise HTTPException(status_code=400, detail="Invalid area_id format")
    
    # Calculate score
    score_result = scorer.calculate_score(features, concept)
    
    # Calculate trust metrics
    coverage = TrustMetrics.calculate_coverage(features)
    confidence = TrustMetrics.calculate_confidence(
        score_components=score_result["score_components"],
        coverage=coverage
    )
    
    # Generate "why" bullets
    why_bullets = TrustMetrics.generate_why_bullets(features, score_result["score_components"])
    
    # Generate insights
    strengths, risks = _generate_insights(features, score_result, concept)
    
    # Find nearby alternatives (stub - would query other areas)
    nearby_alternatives = []
    
    # Method info
    method_info = TrustMetrics.get_method_info(
        scoring_method="heuristic",
        features_used=features
    )
    
    from models.schemas import AreaDetailResponse, AvailableProperty
    
    return AreaDetailResponse(
        area_id=area_id,
        area_name=area_name,
        city=city,
        score=score_result["score"],
        predicted_revenue_low=score_result["revenue_low"],
        predicted_revenue_mid=score_result["revenue_mid"],
        predicted_revenue_high=score_result["revenue_high"],
        confidence=confidence,
        coverage=coverage,
        method=method_info,
        available_properties=[],  # Would fetch from property API
        why=why_bullets,
        demographics={
            "population_1km": features.get("population_1km"),
            "population_density": features.get("population_density"),
            "median_income": features.get("median_income"),
            "higher_education_percent": features.get("higher_education_percent")
        },
        competition_analysis={
            "competitors_count": features.get("competitors_count"),
            "competitors_per_1k_residents": features.get("competitors_per_1k_residents"),
            "nearest_competitor_distance": min(
                [c.get("distance", 9999) for c in features.get("competitors", [])],
                default=None
            )
        },
        traffic_access={
            "nearest_metro_distance_m": features.get("nearest_metro_distance_m"),
            "nearest_tram_distance_m": features.get("nearest_tram_distance_m"),
            "walkability_poi_count": features.get("walkability_poi_count")
        },
        latitude=lat,
        longitude=lng,
        strengths=strengths,
        risks=risks,
        nearby_alternatives=nearby_alternatives
    )


# ============= Site Analysis Endpoint =============

@app.post("/api/analyze", response_model=SiteAnalysisResponse)
async def analyze_sites(request: SiteAnalysisRequest):
    """
    Analyze one or more specific addresses using Agno multi-agent reasoning

    NEW: Uses Orchestrator agent to coordinate GEO, DEMO, COMP, TRANSIT, RISK, and REVENUE specialists
    Provides transparent reasoning traces for every prediction.
    """
    if not request.addresses:
        raise HTTPException(status_code=400, detail="At least one address required")

    if len(request.addresses) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 addresses allowed")

    predictions = []

    for address in request.addresses:
        try:
            print(f"\n🔍 Analyzing: {address}")

            # Collect raw data from all sources
            features = await data_collector.collect_site_data(address, request.concept)

            # NEW: Use Agno Orchestrator for reasoning-based analysis
            analysis = await orchestrator.analyze_site(
                address=address,
                concept=request.concept,
                raw_data={
                    "postal_code": features.get("postal_code"),
                    "demographics": {
                        "population": features.get("population_1km"),
                        "median_income": features.get("median_income"),
                        "mean_income": features.get("mean_income"),
                        "age_15_64_percent": features.get("age_18_24_percent"),  # Approximation
                        "higher_education_percent": features.get("higher_education_percent"),
                    } if features.get("median_income") else None,
                    "population_grid": {
                        "total_population": features.get("population_1km"),
                        "population_density": features.get("population_density"),
                    },
                    "competitors": features.get("competitors", []),
                    "transit": {
                        "nearest_metro_distance_m": features.get("nearest_metro_distance_m"),
                        "nearest_tram_distance_m": features.get("nearest_tram_distance_m"),
                        "metro_stations": features.get("metro_stations", []),
                        "tram_stops": features.get("tram_stops", []),
                    },
                    "walkability_poi_count": features.get("walkability_poi_count", 0),
                },
                data_services={
                    "geocoder": geocoding_service
                }
            )

            # Extract revenue prediction
            revenue = analysis["revenue_analysis"]

            # Map orchestrator results to SitePrediction schema
            prediction = SitePrediction(
                address=address,
                latitude=analysis["geo_analysis"]["latitude"],
                longitude=analysis["geo_analysis"]["longitude"],
                postal_code=analysis["geo_analysis"].get("postal_code"),
                score=analysis["opportunity_score"],
                predicted_revenue_low=revenue["revenue_range"]["pessimistic"],
                predicted_revenue_mid=revenue["revenue_range"]["realistic"],
                predicted_revenue_high=revenue["revenue_range"]["optimistic"],
                confidence=analysis["confidence"],
                recommendation=analysis["recommendation"],
                strengths=analysis["key_strengths"],
                risks=analysis["key_concerns"],
                features=SiteFeatures(
                    population_1km=features.get("population_1km"),
                    population_density=features.get("population_density"),
                    median_income=features.get("median_income"),
                    age_18_24_percent=features.get("age_18_24_percent"),
                    competitors_count=features.get("competitors_count"),
                    competitors_per_1k_residents=features.get("competitors_per_1k_residents"),
                    nearest_metro_distance_m=features.get("nearest_metro_distance_m"),
                    nearest_tram_distance_m=features.get("nearest_tram_distance_m"),
                    walkability_score=features.get("walkability_poi_count"),
                    # NEW: Agent-based scores
                    population_score=analysis["demographic_analysis"]["demographic_score"],
                    income_score=analysis["demographic_analysis"]["demographic_score"],  # Using demo score
                    access_score=analysis["transit_analysis"]["transit_score"],
                    competition_score=analysis["competition_analysis"]["competition_score"],
                    walkability_score_component=analysis["transit_analysis"]["walkability_score"]
                ),
                # NEW: Include reasoning traces for transparency
                reasoning_summary=analysis["executive_summary"],
                agent_reasoning={
                    "geo": analysis["reasoning_traces"].get("geo"),
                    "demographics": analysis["reasoning_traces"].get("demographics"),
                    "competition": analysis["reasoning_traces"].get("competition"),
                    "transit": analysis["reasoning_traces"].get("transit"),
                    "risk": analysis["reasoning_traces"].get("risk"),
                    "revenue": analysis["reasoning_traces"].get("revenue"),
                }
            )

            predictions.append(prediction)

        except Exception as e:
            import traceback
            print(f"❌ Error analyzing {address}:")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error analyzing address: {str(e)}")

    # Rank predictions if multiple sites
    ranking = None
    if len(predictions) > 1:
        sorted_predictions = sorted(enumerate(predictions), key=lambda x: x[1].score, reverse=True)
        ranking = [idx for idx, _ in sorted_predictions]

        # Add rank to each prediction
        for rank, (original_idx, _) in enumerate(sorted_predictions):
            predictions[original_idx].rank = rank + 1

    # Check for cannibalization
    cannibalization_warning = _check_cannibalization(predictions)

    return SiteAnalysisResponse(
        concept=request.concept,
        sites=predictions,
        ranking=ranking,
        cannibalization_warning=cannibalization_warning,
        prediction_id=f"pred_{hash(str(predictions))}"  # Simple ID for MVP
    )


def _generate_insights(features: Dict[str, Any], score_result: Dict[str, Any], concept: str) -> tuple[List[str], List[str]]:
    """Generate strengths and risks from features"""

    strengths = []
    risks = []

    # Population insights
    if features.get("population_density", 0) > 10000:
        strengths.append(f"High population density ({int(features['population_density'])}/km²)")
    elif features.get("population_density", 0) < 3000:
        risks.append(f"Low population density ({int(features['population_density'])}/km²)")

    # Income insights
    if features.get("median_income", 0) > 55000:
        strengths.append(f"High-income area (€{int(features['median_income']):,} median)")
    elif features.get("median_income", 0) < 35000:
        risks.append(f"Lower-income area (€{int(features['median_income']):,} median)")

    # Transit insights
    metro_dist = features.get("nearest_metro_distance_m")
    if metro_dist and metro_dist < 300:
        strengths.append(f"Excellent metro access ({int(metro_dist)}m)")
    elif metro_dist and metro_dist > 800:
        risks.append(f"Limited metro access ({int(metro_dist)}m)")

    # Competition insights
    comp_count = features.get("competitors_count", 0)
    if comp_count < 3:
        strengths.append(f"Low competition ({comp_count} nearby competitors)")
    elif comp_count > 10:
        risks.append(f"High competition ({comp_count} nearby competitors)")

    # Young demographic
    if features.get("age_18_24_percent", 0) > 15:
        strengths.append(f"Young demographic ({features['age_18_24_percent']:.1f}% age 18-24)")

    return strengths[:5], risks[:5]  # Limit to top 5 each


def _check_cannibalization(predictions: List[SitePrediction]) -> str:
    """Check if any sites are too close together"""

    if len(predictions) < 2:
        return None

    from math import radians, sin, cos, sqrt, atan2

    def distance_km(lat1, lng1, lat2, lng2):
        R = 6371
        dlat = radians(lat2 - lat1)
        dlng = radians(lng2 - lng1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    warnings = []
    for i in range(len(predictions)):
        for j in range(i + 1, len(predictions)):
            dist = distance_km(
                predictions[i].latitude, predictions[i].longitude,
                predictions[j].latitude, predictions[j].longitude
            )
            if dist < 2.0:  # Within 2km
                warnings.append(f"Sites {i+1} and {j+1} are {dist:.1f}km apart")

    return "; ".join(warnings) if warnings else None


# ============= Outcome Tracking =============

@app.post("/api/outcomes", response_model=OutcomeResponse)
async def submit_outcome(
    outcome: OutcomeSubmission,
    db: Session = Depends(get_db)
):
    """
    Submit actual revenue after opening
    
    THE MOAT: Every outcome makes predictions better
    - Stores in ConceptTrainingOutcome table
    - Triggers concept re-training (if enough data)
    - Updates base_revenue, weights, uncertainty bands
    """
    from services.concept_learner import ConceptLearner
    from models.database import Prediction, Outcome
    
    # Get prediction
    prediction = db.query(Prediction).filter(
        Prediction.id == int(outcome.prediction_id.replace("pred_", ""))
    ).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail=f"Prediction {outcome.prediction_id} not found")
    
    # Check if outcome already exists
    existing_outcome = db.query(Outcome).filter(
        Outcome.prediction_id == prediction.id
    ).first()
    
    if existing_outcome:
        raise HTTPException(
            status_code=400,
            detail="Outcome already submitted for this prediction"
        )
    
    # Calculate variance
    variance_percent = ((outcome.actual_revenue - prediction.revenue_mid) / prediction.revenue_mid) * 100
    within_band = (prediction.revenue_low <= outcome.actual_revenue <= prediction.revenue_high)
    
    # Store outcome in Outcome table
    new_outcome = Outcome(
        prediction_id=prediction.id,
        actual_revenue=outcome.actual_revenue,
        opening_date=outcome.opening_date,
        variance_percent=variance_percent,
        within_predicted_band="yes" if within_band else "no",
        notes=outcome.notes
    )
    db.add(new_outcome)
    db.commit()
    
    # LEARNING: If prediction has concept_id, trigger concept learning
    learning_result = None
    if prediction.concept_id:
        learner = ConceptLearner(db)
        learning_result = learner.record_outcome(
            prediction_id=prediction.id,
            actual_revenue=outcome.actual_revenue,
            opened_at=outcome.opening_date
        )
    
    # Prepare response message
    if learning_result and learning_result.get("triggered_retraining"):
        message = (
            f"Outcome recorded! This triggered concept re-training. "
            f"New prediction accuracy: {learning_result['new_accuracy']:.1f}% MAPE. "
            f"Total outcomes for this concept: {learning_result['outcomes_count']}."
        )
    else:
        message = "Outcome recorded successfully. Thank you for helping improve our predictions!"
    
    return OutcomeResponse(
        status="recorded",
        variance_percent=round(variance_percent, 2),
        within_predicted_band=within_band,
        message=message
    )


@app.get("/api/accuracy", response_model=AccuracyStats)
async def get_accuracy_stats():
    """
    Get model accuracy statistics
    """
    # In production, calculate from database
    # For MVP, return mock data

    return AccuracyStats(
        total_predictions=42,
        sites_opened=18,
        within_predicted_band=15,
        accuracy_rate=0.83,
        avg_variance_percent=-3.2
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
