# Agent Architecture & Integration

This document details the **Agno multi-agent system** that powers Spotlight's deep analysis mode. It covers each agent's role, inputs, outputs, and how they work together.

---

## Architecture Overview

### Multi-Agent System Design

```
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR AGENT                       │
│  (Coordinates all agents + synthesizes final recommendation) │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
     ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
     │   GEO   │         │  DEMO   │        │  COMP   │
     │  Agent  │         │  Agent  │        │  Agent  │
     └─────────┘         └─────────┘        └─────────┘
          │                   │                   │
          │              ┌────▼────┐              │
          │              │ TRANSIT │              │
          │              │  Agent  │              │
          │              └─────────┘              │
          │                   │                   │
          └───────────────┬───┴───────────────────┘
                          │
                     ┌────▼────┐
                     │  RISK   │
                     │  Agent  │
                     └─────────┘
                          │
                     ┌────▼────┐
                     │ REVENUE │
                     │  Agent  │
                     └─────────┘
```

### Execution Flow

```
1. Data Collection (10s)
   └─ Geocoding, Demographics, Competition, Transit

2. GEO Agent (10s)
   └─ Validates location quality and geocoding confidence

3. DEMO Agent (10s)
   └─ Analyzes demographics vs target customer profile

4. COMP Agent (10s)
   └─ Evaluates competitive landscape and saturation

5. TRANSIT Agent (10s)
   └─ Assesses public transit and walkability

6. RISK Agent (10s)
   └─ Calculates confidence score and identifies risks

7. REVENUE Agent (10s)
   └─ Predicts monthly revenue based on all factors

8. ORCHESTRATOR (10s)
   └─ Synthesizes results into final recommendation

Total: ~70-80 seconds
```

---

## Agent Details

### 1. GEO Agent (Location Validation Specialist)

**File:** [`/backend/agents/agno/geo_agent.py`](../agents/agno/geo_agent.py)

**Purpose:** Validate geocoding accuracy and location quality

**Model:** `openai:gpt-4` with `reasoning=True`

**Input:**
```python
{
    "address": "Mannerheimintie 1, Helsinki",
    "geocoder": <GeocodingService instance>
}
```

**Process:**
1. Geocode address using Digitransit API
2. Validate coordinates exist and are in Finland
3. Extract postal code, municipality, district
4. Assess geocoding confidence based on match quality
5. Identify location quality factors (urban/suburban, accessibility)

**Output:**
```python
{
    "latitude": 60.1699,
    "longitude": 24.9384,
    "postal_code": "00100",
    "municipality": "Helsinki",
    "district": "Kamppi",
    "street_address": "Mannerheimintie 1",
    "geocoding_confidence": "high",  # high/medium/low
    "data_quality_score": 95,  # 0-100
    "location_type": "urban_core",  # urban_core/urban/suburban/rural
    "confidence": "high",
    "reasoning": "Detailed explanation of location validation..."
}
```

**Key Logic:**
```python
# Confidence scoring
if exact_match and postal_code:
    confidence = "high"
    data_quality = 90-100
elif partial_match:
    confidence = "medium"
    data_quality = 60-89
else:
    confidence = "low"
    data_quality = 0-59
```

**Reasoning Example:**
> "The address 'Mannerheimintie 1, Helsinki' geocoded successfully to coordinates (60.1699, 24.9384) in postal code 00100, Kamppi district. This is an exact match with high confidence. The location is in Helsinki's urban core, a highly accessible area with excellent infrastructure. Data quality score: 95/100."

---

### 2. DEMO Agent (Demographics Specialist)

**File:** [`/backend/agents/agno/demo_agent.py`](../agents/agno/demo_agent.py)

**Purpose:** Analyze demographics and match to target customer profile

**Model:** `openai:gpt-4` with `reasoning=True`

**Input:**
```python
{
    "postal_code": "00100",
    "concept": "casual_dining",
    "paavo_data": {...},  # PAAVO demographics
    "population_grid": {...},  # 1km grid data
    "municipality": "Helsinki"
}
```

**Process:**
1. Extract key demographics (population, income, age distribution, education)
2. Compare to target customer profile for concept
3. Assess match quality (excellent/good/fair/poor)
4. Calculate demographic score (0-100)
5. Identify strengths and concerns

**Output:**
```python
{
    "demographic_score": 88,  # 0-100
    "target_match": "excellent",  # excellent/good/fair/poor
    "confidence": "high",
    "population_density": 12500,  # per km²
    "median_income": 42000,  # EUR/year
    "age_distribution": {
        "0-14": 12,
        "15-64": 72,
        "65+": 16
    },
    "education_level": "high",  # 45% higher education
    "customer_profile_match": {
        "income_match": "excellent",
        "age_match": "good",
        "lifestyle_match": "excellent"
    },
    "strengths": [
        "High median income (€42K) supports casual dining price point",
        "72% working-age population drives weekday lunch traffic",
        "Urban professionals align with casual dining target"
    ],
    "concerns": [
        "Limited family demographic may reduce weekend traffic"
    ],
    "reasoning": "Detailed demographic analysis..."
}
```

**Target Profiles by Concept:**

| Concept | Target Income | Target Age | Target Lifestyle |
|---------|--------------|------------|------------------|
| Casual Dining | €35K-60K | 25-54 | Urban professionals, families |
| Fine Dining | €60K+ | 35-65 | Affluent, educated |
| Quick Service | €25K-50K | 18-45 | Students, young professionals |
| Family Restaurant | €30K-55K | 30-55 | Families with children |
| Café | €30K-55K | 20-50 | Students, remote workers |

**Scoring Logic:**
```python
# Income match (40% weight)
if median_income >= target_income * 1.2:
    income_score = 100
elif median_income >= target_income:
    income_score = 85
elif median_income >= target_income * 0.8:
    income_score = 65
else:
    income_score = 40

# Age match (30% weight)
target_age_pct = age_distribution[target_age_range]
age_score = min(target_age_pct * 2, 100)

# Education match (20% weight)
if higher_education_pct >= 40:
    education_score = 100
elif higher_education_pct >= 25:
    education_score = 75
else:
    education_score = 50

# Population density (10% weight)
if pop_density >= 10000:
    density_score = 100
elif pop_density >= 5000:
    density_score = 75
else:
    density_score = 50

demographic_score = (income_score * 0.40 +
                     age_score * 0.30 +
                     education_score * 0.20 +
                     density_score * 0.10)
```

---

### 3. COMP Agent (Competition Specialist)

**File:** [`/backend/agents/agno/comp_agent.py`](../agents/agno/comp_agent.py)

**Purpose:** Analyze competitive landscape and market saturation

**Model:** `openai:gpt-4` with `reasoning=True`

**Input:**
```python
{
    "latitude": 60.1699,
    "longitude": 24.9384,
    "concept": "casual_dining",
    "competitors": [...],  # OSM Overpass results
    "radius_m": 1000
}
```

**Process:**
1. Count competitors by type (direct, indirect, substitute)
2. Calculate market saturation (competitors per 10K people)
3. Assess competitive intensity (low/moderate/high/saturated)
4. Identify competitive advantages and threats
5. Calculate competition score (0-100, where 100 = low competition)

**Output:**
```python
{
    "competition_score": 72,  # 0-100 (higher = less competition)
    "confidence": "high",
    "competitor_count": 18,
    "direct_competitors": 8,  # Same concept
    "indirect_competitors": 6,  # Similar but different
    "substitute_competitors": 4,  # Different format (cafés, fast food)
    "saturation_level": "moderate",  # low/moderate/high/saturated
    "market_saturation_ratio": 1.44,  # competitors per 10K people
    "competitive_intensity": "moderate",
    "nearest_competitor_m": 120,
    "competitive_advantages": [
        "No direct casual dining in 200m radius",
        "Nearest Burger King 350m away",
        "Area underserved for full-service restaurants"
    ],
    "competitive_threats": [
        "18 total competitors may split customer base",
        "Moderate saturation (1.44 per 10K) suggests crowded market"
    ],
    "reasoning": "Detailed competition analysis..."
}
```

**Competitor Classification:**

```python
# Direct competitors (same concept)
"casual_dining": ["restaurant", "bistro", "brasserie"]
"fine_dining": ["fine_dining", "upscale_restaurant"]
"quick_service": ["fast_food", "burger", "pizza"]

# Indirect competitors (similar need, different format)
"casual_dining": ["café", "gastropub", "wine_bar"]

# Substitute competitors (different need solution)
"casual_dining": ["food_court", "food_truck", "deli"]
```

**Saturation Thresholds:**

| Saturation Ratio | Level | Competition Score |
|------------------|-------|-------------------|
| < 0.8 per 10K | Low | 90-100 |
| 0.8-1.5 per 10K | Moderate | 70-89 |
| 1.5-2.5 per 10K | High | 40-69 |
| > 2.5 per 10K | Saturated | 0-39 |

**Scoring Logic:**
```python
# Base score from saturation (60% weight)
if saturation_ratio < 0.8:
    saturation_score = 100
elif saturation_ratio < 1.5:
    saturation_score = 85
elif saturation_ratio < 2.5:
    saturation_score = 60
else:
    saturation_score = 30

# Proximity penalty (40% weight)
if nearest_competitor_m > 300:
    proximity_score = 100
elif nearest_competitor_m > 150:
    proximity_score = 75
elif nearest_competitor_m > 75:
    proximity_score = 50
else:
    proximity_score = 25

competition_score = (saturation_score * 0.60 +
                     proximity_score * 0.40)
```

---

### 4. TRANSIT Agent (Accessibility Specialist)

**File:** [`/backend/agents/agno/transit_agent.py`](../agents/agno/transit_agent.py)

**Purpose:** Assess public transit access and walkability

**Model:** `openai:gpt-4` with `reasoning=True`

**Input:**
```python
{
    "transit_data": {
        "nearest_metro_distance_m": 280,
        "nearest_tram_distance_m": 120,
        "metro_stations": [...],
        "tram_stops": [...]
    },
    "walkability_poi_count": 45,
    "municipality": "Helsinki"
}
```

**Process:**
1. Calculate transit score based on metro/tram proximity
2. Calculate walkability score from POI density
3. Rate transit access (excellent/good/fair/poor)
4. Rate walkability (high/moderate/low)
5. Assess overall accessibility for customers

**Output:**
```python
{
    "transit_score": 88,  # 0-100
    "confidence": "high",
    "nearest_metro_m": 280,
    "nearest_tram_m": 120,
    "metro_stations_nearby": 2,
    "tram_stops_nearby": 3,
    "transit_access_rating": "excellent",  # excellent/good/fair/poor
    "walkability_score": 90,
    "walkability_poi_count": 45,
    "walkability_rating": "high",  # high/moderate/low
    "accessibility_summary": "Excellent public transit access in highly walkable area",
    "insights": [
        "Tram stop 120m away provides excellent access",
        "Metro station 280m ensures high connectivity",
        "45 walkability POIs indicate vibrant pedestrian area"
    ],
    "reasoning": "Detailed transit analysis..."
}
```

**Transit Scoring (70% of total):**

```python
# Metro scoring (0-50 points)
if metro_distance < 200:
    metro_score = 50
elif metro_distance < 300:
    metro_score = 45
elif metro_distance < 400:
    metro_score = 38
elif metro_distance < 500:
    metro_score = 30
elif metro_distance < 600:
    metro_score = 20
else:
    metro_score = 10

# Tram scoring (0-40 points)
if tram_distance < 150:
    tram_score = 40
elif tram_distance < 250:
    tram_score = 35
elif tram_distance < 350:
    tram_score = 28
elif tram_distance < 500:
    tram_score = 20
else:
    tram_score = 10

# Bonus for multiple options (0-10 points)
bonus = min(metro_count + tram_count * 2, 10)

transit_score = metro_score + tram_score + bonus
```

**Walkability Scoring (30% of total):**

```python
# POI-based walkability
if poi_count >= 50:
    walkability = 100
elif poi_count >= 40:
    walkability = 90
elif poi_count >= 30:
    walkability = 75
elif poi_count >= 20:
    walkability = 60
elif poi_count >= 10:
    walkability = 45
else:
    walkability = max(poi_count * 3, 20)
```

**Overall Score:**
```python
overall_score = (transit_score * 0.7) + (walkability_score * 0.3)
```

---

### 5. RISK Agent (Risk Assessment Specialist)

**File:** [`/backend/agents/agno/risk_agent.py`](../agents/agno/risk_agent.py)

**Purpose:** Calculate confidence score and identify risk factors

**Model:** `openai:gpt-4` with `reasoning=True`

**Input:**
```python
{
    "geo_results": {...},
    "demo_results": {...},
    "comp_results": {...},
    "transit_results": {...},
    "revenue_prediction": {...}  # Optional
}
```

**Process:**
1. Extract confidence levels from all agents
2. Calculate overall confidence score (0-100)
3. Assess data quality for each component
4. Identify risk factors (competition, data gaps, demographic mismatches)
5. Determine risk level (low/medium/high)
6. Generate recommendations for additional data collection

**Output:**
```python
{
    "overall_confidence": 82,  # 0-100
    "confidence_rating": "high",  # very high/high/medium/low
    "data_quality_score": 88,  # 0-100
    "risk_level": "low",  # low/medium/high
    "missing_data": [
        "Crime statistics",
        "Foot traffic counts",
        "Parking availability",
        "Rent/lease costs"
    ],
    "risk_factors": [
        {
            "factor": "High competition",
            "severity": "medium",
            "description": "18 competitors in 1km radius"
        }
    ],
    "data_coverage": {
        "geocoding": 95,
        "demographics": 90,
        "competition": 85,
        "transit": 88
    },
    "reasoning": "Detailed risk assessment...",
    "recommendations": [
        "Consider collecting peak-hour foot traffic data",
        "Conduct competitive differentiation analysis"
    ],
    "transparency_warning": "Note: Medium confidence prediction. Consider additional market research to validate findings."
}
```

**Confidence Calculation:**

```python
# Convert text confidence to numeric
confidence_scores = {
    "high": 90,
    "medium": 70,
    "low": 40
}

# Weight each agent equally (for now)
avg_confidence = (
    confidence_scores[geo_confidence] +
    confidence_scores[demo_confidence] +
    confidence_scores[comp_confidence] +
    confidence_scores[transit_confidence]
) / 4

# Adjust based on data quality
data_quality_avg = (
    geo_quality +
    demo_score +
    comp_score +
    transit_score
) / 4

overall_confidence = (avg_confidence * 0.6) + (data_quality_avg * 0.4)
```

**Risk Factor Detection:**

```python
risk_factors = []

# High competition
if competitor_count > 20:
    risk_factors.append({
        "factor": "High competition",
        "severity": "medium",
        "description": f"{competitor_count} competitors in 1km radius"
    })

# Poor transit access
if transit_access_rating == "poor":
    risk_factors.append({
        "factor": "Limited transit access",
        "severity": "medium",
        "description": "Poor public transit connectivity"
    })

# Demographic mismatch
if demo_score < 60:
    risk_factors.append({
        "factor": "Demographic mismatch",
        "severity": "high",
        "description": "Demographics below target for concept"
    })

# Low data quality
if overall_confidence < 70:
    risk_factors.append({
        "factor": "Data quality concerns",
        "severity": "medium",
        "description": "Limited data availability affects prediction confidence"
    })
```

**Risk Level Determination:**

```python
if overall_confidence >= 80 and len(risk_factors) < 2:
    risk_level = "low"
elif overall_confidence >= 65 and len(risk_factors) < 3:
    risk_level = "medium"
else:
    risk_level = "high"
```

---

### 6. REVENUE Agent (Revenue Prediction Specialist)

**File:** [`/backend/agents/agno/revenue_agent.py`](../agents/agno/revenue_agent.py)

**Purpose:** Predict monthly revenue based on all factors

**Model:** `openai:gpt-4` with `reasoning=True`

**Input:**
```python
{
    "concept": "casual_dining",
    "geo_results": {...},
    "demo_results": {...},
    "comp_results": {...},
    "transit_results": {...},
    "risk_results": {...}
}
```

**Process:**
1. Get concept baseline parameters (avg check, daily covers, operating days)
2. Calculate base revenue from baseline
3. Apply demographic adjustment (35% weight)
4. Apply competition adjustment (25% weight)
5. Apply transit adjustment (20% weight)
6. Apply location quality adjustment (20% weight)
7. Generate revenue range (pessimistic, realistic, optimistic)
8. Identify key revenue drivers

**Output:**
```python
{
    "predicted_monthly_revenue": 145000,  # EUR
    "opportunity_score": 85,  # 0-100
    "revenue_range": {
        "pessimistic": 94250,   # 65% of realistic
        "realistic": 145000,
        "optimistic": 174000    # 120% of realistic
    },
    "confidence": "high",
    "key_drivers": [
        {
            "factor": "Demographics",
            "impact": "+35%",
            "reasoning": "High-income professionals support premium pricing"
        },
        {
            "factor": "Transit Access",
            "impact": "+18%",
            "reasoning": "Excellent metro/tram access drives foot traffic"
        },
        {
            "factor": "Competition",
            "impact": "-8%",
            "reasoning": "18 competitors may dilute market share"
        }
    ],
    "breakdown": {
        "base_revenue": 112000,
        "demographic_adjustment": +39200,
        "competition_adjustment": -8960,
        "transit_adjustment": +20160,
        "location_adjustment": +22400
    },
    "reasoning": "Detailed revenue prediction..."
}
```

**Concept Baselines:**

```python
CONCEPT_PARAMS = {
    "casual_dining": {
        "avg_check": 28,  # EUR
        "daily_covers": 120,  # customers per day
        "operating_days": 26  # days per month
    },
    "fine_dining": {
        "avg_check": 85,
        "daily_covers": 50,
        "operating_days": 24
    },
    "quick_service": {
        "avg_check": 12,
        "daily_covers": 200,
        "operating_days": 28
    },
    "family_restaurant": {
        "avg_check": 32,
        "daily_covers": 100,
        "operating_days": 26
    }
}
```

**Revenue Calculation:**

```python
# Step 1: Base revenue
base_revenue = avg_check × daily_covers × operating_days

# Step 2: Factor adjustments (weighted)
demo_adjustment = (demo_score - 50) / 50 × 0.35
comp_adjustment = (comp_score - 50) / 50 × 0.25
transit_adjustment = (transit_score - 50) / 50 × 0.20
location_adjustment = (confidence - 50) / 50 × 0.20

total_adjustment = (
    demo_adjustment +
    comp_adjustment +
    transit_adjustment +
    location_adjustment
)

# Step 3: Apply adjustment
realistic_revenue = base_revenue × (1 + total_adjustment)

# Step 4: Generate range
pessimistic = realistic × 0.65
optimistic = realistic × 1.20
```

**Opportunity Score:**

```python
# Normalize revenue against concept median
concept_median = {
    "casual_dining": 120000,
    "fine_dining": 100000,
    "quick_service": 150000
}

normalized_score = (realistic_revenue / concept_median[concept]) × 100
opportunity_score = min(normalized_score, 100)
```

---

### 7. ORCHESTRATOR Agent (Synthesis & Coordination)

**File:** [`/backend/agents/agno/orchestrator.py`](../agents/agno/orchestrator.py)

**Purpose:** Coordinate all agents and synthesize final recommendation

**Model:** `openai:gpt-4` with `reasoning=True`

**Role:**
1. Execute agents in sequence
2. Pass results between agents
3. Handle agent failures with fallbacks
4. Synthesize final recommendation
5. Generate executive summary
6. Compile reasoning traces from all agents

**Key Method:**

```python
async def analyze_site(
    self,
    address: str,
    concept: str,
    raw_data: Dict[str, Any],
    data_services: Dict[str, Any]
) -> Dict[str, Any]:
    """Orchestrate comprehensive site analysis"""

    # Step 1: GEO Agent
    geo_results = await self.geo_agent.geocode_and_validate(
        address=address,
        geocoder=data_services["geocoder"]
    )

    # Step 2: DEMO Agent
    demo_results = await self.demo_agent.analyze_demographics(
        postal_code=geo_results["postal_code"],
        concept=concept,
        paavo_data=raw_data["demographics"],
        population_grid=raw_data["population_grid"],
        municipality=geo_results["municipality"]
    )

    # Step 3: COMP Agent
    comp_results = await self.comp_agent.analyze_competition(
        latitude=geo_results["latitude"],
        longitude=geo_results["longitude"],
        concept=concept,
        competitors=raw_data["competitors"],
        radius_m=1000
    )

    # Step 4: TRANSIT Agent
    transit_results = await self.transit_agent.analyze_transit(
        transit_data=raw_data["transit"],
        walkability_poi_count=raw_data.get("walkability_pois", 0),
        municipality=geo_results["municipality"]
    )

    # Step 5: RISK Agent
    risk_results = await self.risk_agent.assess_risk_and_confidence(
        geo_results=geo_results,
        demo_results=demo_results,
        comp_results=comp_results,
        transit_results=transit_results
    )

    # Step 6: REVENUE Agent
    revenue_results = await self.revenue_agent.predict_revenue(
        concept=concept,
        geo_results=geo_results,
        demo_results=demo_results,
        comp_results=comp_results,
        transit_results=transit_results,
        risk_results=risk_results
    )

    # Step 7: Synthesis
    synthesis = await self._synthesize_final_recommendation(
        address=address,
        concept=concept,
        geo_results=geo_results,
        demo_results=demo_results,
        comp_results=comp_results,
        transit_results=transit_results,
        risk_results=risk_results,
        revenue_results=revenue_results
    )

    # Compile final response
    return {
        "address": address,
        "concept": concept,
        "opportunity_score": revenue_results["opportunity_score"],
        "predicted_monthly_revenue": revenue_results["predicted_monthly_revenue"],
        "revenue_range": revenue_results["revenue_range"],
        "confidence": risk_results["overall_confidence"],
        "confidence_rating": risk_results["confidence_rating"],
        "risk_level": risk_results["risk_level"],
        "recommendation": synthesis["recommendation"],
        "executive_summary": synthesis["executive_summary"],
        "location": {
            "latitude": geo_results["latitude"],
            "longitude": geo_results["longitude"],
            "postal_code": geo_results["postal_code"],
            "municipality": geo_results["municipality"]
        },
        "scores": {
            "demographic_score": demo_results["demographic_score"],
            "competition_score": comp_results["competition_score"],
            "transit_score": transit_results["transit_score"],
            "data_quality_score": risk_results["data_quality_score"]
        },
        "reasoning_traces": {
            "geo": geo_results["reasoning"],
            "demographics": demo_results["reasoning"],
            "competition": comp_results["reasoning"],
            "transit": transit_results["reasoning"],
            "risk": risk_results["reasoning"],
            "revenue": revenue_results["reasoning"],
            "synthesis": synthesis["reasoning"]
        },
        "insights": {
            "demographic_strengths": demo_results.get("strengths", []),
            "demographic_concerns": demo_results.get("concerns", []),
            "competitive_advantages": comp_results.get("competitive_advantages", []),
            "competitive_threats": comp_results.get("competitive_threats", []),
            "transit_insights": transit_results.get("insights", []),
            "key_drivers": revenue_results.get("key_drivers", [])
        },
        "risk_assessment": {
            "risk_factors": risk_results["risk_factors"],
            "missing_data": risk_results["missing_data"],
            "recommendations": risk_results["recommendations"],
            "transparency_warning": risk_results.get("transparency_warning")
        }
    }
```

**Synthesis Logic:**

```python
async def _synthesize_final_recommendation(self, **all_results):
    """Generate executive summary and recommendation"""

    # Build synthesis prompt
    prompt = f"""
    Synthesize a final recommendation for this restaurant site:

    PREDICTED REVENUE: €{revenue_results['predicted_monthly_revenue']:,}/month
    OPPORTUNITY SCORE: {revenue_results['opportunity_score']}/100
    CONFIDENCE: {risk_results['overall_confidence']}% ({risk_results['confidence_rating']})
    RISK LEVEL: {risk_results['risk_level']}

    KEY STRENGTHS:
    {self._format_list(demo_results['strengths'] + comp_results['competitive_advantages'])}

    KEY CONCERNS:
    {self._format_list(demo_results['concerns'] + comp_results['competitive_threats'])}

    PROVIDE:
    1. Executive Summary (3-4 sentences)
    2. Clear Recommendation (MAKE OFFER / NEGOTIATE / PASS)
    3. Top 3 Supporting Points
    4. Top 2 Risk Factors
    5. Next Steps
    """

    response = self.run(prompt)

    return {
        "executive_summary": extract_summary(response),
        "recommendation": extract_recommendation(response),
        "reasoning": response.content
    }
```

---

## Integration Points

### API Endpoint Integration

**File:** [`/backend/main.py`](../main.py)

**Current State (COMMENTED OUT):**

```python
# Line 31 (COMMENTED OUT):
# from agents.agno.orchestrator import OrchestratorAgent

# Line 61 (COMMENTED OUT):
# orchestrator = OrchestratorAgent()
```

**Should Be:**

```python
from agents.agno.orchestrator import OrchestratorAgent

orchestrator = OrchestratorAgent()

@app.post("/api/analyze")
async def analyze_site(request: AnalyzeRequest):
    """Deep analysis using Agno agents"""

    # Phase 1: Data collection (10s)
    features = await data_collector.collect_site_data(
        address=request.address,
        concept=request.concept
    )

    # Phase 2: Agno agent analysis (60-70s)
    analysis = await orchestrator.analyze_site(
        address=request.address,
        concept=request.concept,
        raw_data={
            "demographics": features.get("demographics"),
            "population_grid": features.get("population_grid"),
            "competitors": features.get("competitors"),
            "transit": features.get("transit"),
            "walkability_pois": features.get("walkability_pois", 0)
        },
        data_services={
            "geocoder": geocoding_service
        }
    )

    return SitePrediction(**analysis)
```

---

## Performance Characteristics

### Latency Budget

| Agent | Expected Time | Max Timeout | Fallback |
|-------|---------------|-------------|----------|
| GEO | 8-12s | 30s | Deterministic geocoding |
| DEMO | 8-12s | 30s | Simple income/density score |
| COMP | 8-12s | 30s | Simple saturation ratio |
| TRANSIT | 8-12s | 30s | Simple proximity score |
| RISK | 8-12s | 30s | Average of available scores |
| REVENUE | 10-15s | 30s | Baseline revenue only |
| ORCHESTRATOR | 10-15s | 30s | No synthesis, return raw scores |

**Total Expected:** 70-90 seconds
**Total Maximum:** 210 seconds (3.5 minutes)

### Cost Estimation

**Assumptions:**
- Model: `openai:gpt-4`
- Input: ~2,000 tokens per agent (context + prompt)
- Output: ~500 tokens per agent (reasoning + results)
- Reasoning: 2x token multiplier

**Per-Agent Cost:**
```
Input: 2,000 tokens × $0.03/1K = $0.06
Output: 500 tokens × $0.06/1K = $0.03
Reasoning: 2x multiplier = $0.18 per agent
```

**Total Cost Per Analysis:**
```
7 agents × $0.18 = $1.26 per address analysis
```

**Monthly Cost Estimates:**

| Plan | Analyses/Month | Total Cost |
|------|----------------|------------|
| Basic (10 analyses) | 10 | $12.60 |
| Pro (100 analyses) | 100 | $126.00 |
| Enterprise (1000 analyses) | 1000 | $1,260.00 |

---

## Error Handling

### Agent Timeout Handling

```python
async def run_agent_with_fallback(agent, method, *args, **kwargs):
    """Run agent with timeout and fallback"""
    try:
        result = await asyncio.wait_for(
            getattr(agent, method)(*args, **kwargs),
            timeout=30
        )
        return result, None

    except asyncio.TimeoutError:
        logger.error(f"{agent.name} timed out after 30s")
        fallback = get_fallback_result(agent.name, *args, **kwargs)
        return fallback, "timeout"

    except Exception as e:
        logger.error(f"{agent.name} failed: {e}")
        fallback = get_fallback_result(agent.name, *args, **kwargs)
        return fallback, str(e)
```

### Partial Failure Handling

```python
# If 1-2 agents fail → Use fallbacks, reduce confidence
if failed_agents <= 2:
    confidence = max(base_confidence - (failed_agents * 15), 40)
    warning = f"{failed_agents} agents failed, using fallback scoring"

# If 3+ agents fail → Return error
else:
    raise HTTPException(
        status_code=500,
        detail="Multiple agent failures, please try again"
    )
```

---

## Future Enhancements

### 1. Parallel Agent Execution

Currently agents run sequentially. Future: Run DEMO, COMP, TRANSIT in parallel (they don't depend on each other).

```python
# Current: ~70s (sequential)
geo → demo → comp → transit → risk → revenue → orchestrator

# Future: ~40s (parallel where possible)
geo → [demo, comp, transit] → risk → revenue → orchestrator
```

### 2. Streaming Results

Return partial results as agents complete:

```python
async def analyze_site_streaming(address, concept):
    yield {"status": "geocoding", "progress": 10}
    geo = await geo_agent.run()

    yield {"status": "analyzing_demographics", "progress": 30}
    demo = await demo_agent.run()

    # ... continue yielding progress
```

### 3. Agent Result Caching

Cache agent results for 24 hours (address + concept):

```python
cache_key = f"{address}:{concept}"
cached = redis.get(cache_key)
if cached:
    return cached  # Skip agents entirely
```

### 4. Adaptive Agent Selection

Skip low-value agents based on initial results:

```python
if geo_confidence == "low":
    # Don't waste time on other agents
    return early_exit_response()

if demo_score < 40:
    # Demographics too poor, skip revenue prediction
    return "not_recommended" response
```

---

## Summary

The Agno multi-agent system provides:

✅ **Transparent reasoning** - Every prediction explained step-by-step
✅ **Specialist expertise** - Each agent focuses on one domain
✅ **Confidence scoring** - Risk assessment for every prediction
✅ **Graceful degradation** - Fallbacks when agents fail
✅ **Scalable architecture** - Easy to add new agents or data sources

**Trade-offs:**
- 70-90 second latency (vs 3 seconds for pre-scoring)
- $1.26 cost per analysis (vs $0.02 for deterministic)
- Requires OpenAI API key

**When to use:**
- Address evaluation (investment decisions)
- Address comparison (rank 2-3 sites)
- Broker proposals (need defensible reasoning)

**When NOT to use:**
- City exploration (use pre-scoring)
- Quick browsing (use pre-scoring)
- 10+ address comparisons (too expensive)
