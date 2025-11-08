# Spotlight API Flows

**Detailed flow for every user action → API call → response**

---

## Flow 1: Search City → Discovery

**User Action:** Types "Helsinki" and presses Enter

### Step 1: Detect Search Type

**Frontend:**
```typescript
const response = await fetch('/api/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'Helsinki' })
});
```

**Backend (`/api/search`):**
```python
def _detect_search_type(query: str) -> str:
    # "Helsinki" has no numbers, <=2 words
    if len(query.split()) <= 2 and not re.search(r'\d', query):
        return "city"
```

**Response:**
```json
{
  "search_type": "discovery",
  "city": "Helsinki",
  "addresses": null,
  "requires_concept": true
}
```

### Step 2: Show Concept Selection

**Frontend:**
- Navigates to `/discover`
- Shows concept buttons: QSR, Fast Casual, Coffee Shop, Casual Dining, Fine Dining
- User clicks "Casual Dining"

### Step 3: Fetch Discovery Data

**Frontend:**
```typescript
const response = await fetch('/api/discover', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    city: 'Helsinki',
    concept: 'casual_dining'
  })
});
```

**Backend (`/api/discover`):**

```python
@app.post("/api/discover")
async def discover_opportunities(request: DiscoveryRequest):
    # 1. Check if city is postal code
    if re.match(r'^\d{5}$', request.city.strip()):
        return await _analyze_postal_area(request.city, request.concept)

    # 2. Get pre-defined areas for city
    if request.city.lower() in ["helsinki", "espoo", "vantaa"]:
        helsinki_areas = _get_helsinki_areas()  # Returns 8 hardcoded areas
    else:
        raise HTTPException(501, "City not supported yet")

    # 3. Score each area
    scored_areas = []
    for area in helsinki_areas:
        # Collect data
        features = await data_collector.collect_area_data(
            area["name"],
            area["lat"],
            area["lng"],
            request.concept
        )

        # Calculate score using OLD SCORER (not agents)
        score_result = scorer.calculate_score(features, request.concept)

        scored_areas.append({
            "area_id": f"helsinki_{area['id']}",
            "area_name": area["name"],
            "score": score_result["score"],
            "latitude": area["lat"],
            "longitude": area["lng"],
            "predicted_revenue_low": score_result["revenue_low"],
            "predicted_revenue_high": score_result["revenue_high"],
            "estimated_rent_psqft": area["rent_psqft"],
            "available_properties_count": area["properties_count"]
        })

    # 4. Sort by score
    scored_areas.sort(key=lambda x: x["score"], reverse=True)

    # 5. Return heatmap + top 10
    return {
        "city": "Helsinki",
        "concept": "casual_dining",
        "heatmap_data": [...],  # All areas for map
        "top_opportunities": scored_areas[:10],  # Top 10
        "total_areas_scored": 8
    }
```

**Response:**
```json
{
  "city": "Helsinki",
  "concept": "casual_dining",
  "heatmap_data": [
    {
      "latitude": 60.1699,
      "longitude": 24.9342,
      "score": 54.4,
      "weight": 0.544
    },
    ...
  ],
  "top_opportunities": [
    {
      "area_id": "helsinki_kamppi",
      "area_name": "Kamppi",
      "score": 54.4,
      "latitude": 60.1699,
      "longitude": 24.9342,
      "predicted_revenue_low": 935000,
      "predicted_revenue_high": 1265000,
      "estimated_rent_psqft": 42,
      "available_properties_count": 3
    },
    ...
  ],
  "total_areas_scored": 8
}
```

**Frontend:**
- Renders map with heatmap layer
- Shows top 10 opportunities list

**Performance:** ~2 seconds total

---

## Flow 2: Search Postal Code → Discovery

**User Action:** Types "00100" and presses Enter

### Step 1: Detect Search Type

**Frontend:**
```typescript
const response = await fetch('/api/search', {
  method: 'POST',
  body: JSON.stringify({ query: '00100' })
});
```

**Backend:**
```python
def _detect_search_type(query: str) -> str:
    # "00100" matches 5-digit pattern
    if re.match(r'^\d{5}$', query.strip()):
        return "postal_code"
```

**Response:**
```json
{
  "search_type": "discovery",
  "city": "00100",  // Pass postal code as "city"
  "addresses": null,
  "requires_concept": true
}
```

### Step 2: Show Concept Selection

(Same as Flow 1)

### Step 3: Fetch Postal Area Data

**Frontend:**
```typescript
const response = await fetch('/api/discover', {
  method: 'POST',
  body: JSON.stringify({
    city: '00100',
    concept: 'casual_dining'
  })
});
```

**Backend (`/api/discover` → `_analyze_postal_area`):**

```python
async def _analyze_postal_area(postal_code: str, concept: str):
    # 1. Fetch demographics from PAAVO
    demographics = await data_collector.statfin.get_demographics_by_postal_code(postal_code)

    if not demographics:
        raise HTTPException(404, "Postal code not found")

    # 2. Get coordinates
    lat = demographics.get("latitude")
    lng = demographics.get("longitude")
    area_name = demographics.get("area_name", postal_code)

    # 3. Collect location data (competition, transit, etc.)
    features = await data_collector.collect_area_data(area_name, lat, lng, concept)

    # 4. Merge PAAVO demographics
    features.update({
        "postal_code": postal_code,
        "median_income": demographics.get("median_income"),
        "mean_income": demographics.get("mean_income"),
        "age_0_14_percent": demographics.get("age_0_14_percent"),
        ...
    })

    # 5. Calculate score
    score_result = scorer.calculate_score(features, concept)

    # 6. Return single-point discovery response
    return {
        "city": f"{area_name} ({postal_code})",
        "concept": concept,
        "heatmap_data": [{
            "latitude": lat,
            "longitude": lng,
            "score": score_result["score"],
            "weight": score_result["score"] / 100
        }],
        "top_opportunities": [{
            "area_id": f"postal_{postal_code}",
            "area_name": f"{area_name} ({postal_code})",
            "score": score_result["score"],
            "latitude": lat,
            "longitude": lng,
            "predicted_revenue_low": score_result["revenue_low"],
            "predicted_revenue_high": score_result["revenue_high"],
            "estimated_rent_psqft": 0,
            "available_properties_count": 0
        }],
        "total_areas_scored": 1
    }
```

**Frontend:**
- Renders map centered on postal code area
- Shows single opportunity

**Performance:** ~3-5 seconds (PAAVO API call + data collection)

---

## Flow 3: Search Single Address → Analysis

**User Action:** Types "Mannerheimintie 1, Helsinki" and presses Enter

### Step 1: Detect Search Type

**Frontend:**
```typescript
const response = await fetch('/api/search', {
  method: 'POST',
  body: JSON.stringify({ query: 'Mannerheimintie 1, Helsinki' })
});
```

**Backend:**
```python
def _detect_search_type(query: str) -> str:
    # Contains numbers + letters (address pattern)
    if re.search(r'\d+\s+[A-Za-zäöåÄÖÅ]+', query):
        return "single_address"
```

**Response:**
```json
{
  "search_type": "single_site",
  "city": null,
  "addresses": ["Mannerheimintie 1, Helsinki"],
  "requires_concept": true
}
```

### Step 2: Show Concept Selection

(Same as previous flows)

### Step 3: Analyze Address (WITH AGNO AGENTS)

**Frontend:**
```typescript
const response = await fetch('/api/analyze', {
  method: 'POST',
  body: JSON.stringify({
    addresses: ['Mannerheimintie 1, Helsinki'],
    concept: 'casual_dining'
  })
});
```

**Backend (`/api/analyze`):**

**⚠️ CURRENT STATUS: AGENTS DISABLED (commented out)**

```python
@app.post("/api/analyze")
async def analyze_sites(request: SiteAnalysisRequest):
    predictions = []

    for address in request.addresses:
        # PHASE 1: Data Collection
        features = await data_collector.collect_site_data(address, request.concept)
        # Returns:
        # - latitude, longitude, postal_code (from Digitransit)
        # - demographics (from PAAVO)
        # - population_density (from Statistics Finland grid)
        # - competitors, transit, walkability (from OSM)

        # PHASE 2: Agno Agent Analysis
        # ⚠️ CURRENTLY COMMENTED OUT - SHOULD BE:
        analysis = await orchestrator.analyze_site(
            address=address,
            concept=request.concept,
            raw_data={
                "postal_code": features.get("postal_code"),
                "demographics": {...},
                "population_grid": {...},
                "competitors": [...],
                "transit": {...},
                "walkability_poi_count": 45
            },
            data_services={"geocoder": geocoding_service}
        )

        # Orchestrator coordinates 7 agents:
        # 1. GEO Agent → Validates location
        # 2. DEMO Agent → Analyzes demographics
        # 3. COMP Agent → Analyzes competition
        # 4. TRANSIT Agent → Analyzes accessibility
        # 5. RISK Agent → Calculates confidence
        # 6. REVENUE Agent → Predicts revenue
        # 7. ORCHESTRATOR → Synthesizes recommendation

        # PHASE 3: Build Response
        prediction = SitePrediction(
            address=address,
            latitude=analysis["geo_analysis"]["latitude"],
            longitude=analysis["geo_analysis"]["longitude"],
            postal_code=analysis["geo_analysis"]["postal_code"],
            score=analysis["opportunity_score"],  # 0-100
            predicted_revenue_low=analysis["revenue_analysis"]["revenue_range"]["pessimistic"],
            predicted_revenue_mid=analysis["revenue_analysis"]["revenue_range"]["realistic"],
            predicted_revenue_high=analysis["revenue_analysis"]["revenue_range"]["optimistic"],
            confidence=analysis["confidence"],  # 0-100
            recommendation=analysis["recommendation"],  # "Highly Recommended" / "Pass"
            strengths=analysis["key_strengths"],  # ["High density", ...]
            risks=analysis["key_concerns"],  # ["High competition", ...]
            reasoning_summary=analysis["executive_summary"],
            agent_reasoning={
                "geo": analysis["reasoning_traces"]["geo"],
                "demographics": analysis["reasoning_traces"]["demographics"],
                "competition": analysis["reasoning_traces"]["competition"],
                "transit": analysis["reasoning_traces"]["transit"],
                "risk": analysis["reasoning_traces"]["risk"],
                "revenue": analysis["reasoning_traces"]["revenue"]
            }
        )

        predictions.append(prediction)

    return {
        "concept": "casual_dining",
        "sites": predictions,
        "ranking": None,  # Only for multiple addresses
        "prediction_id": "pred_abc123"
    }
```

**Agent Execution Timeline:**

```
0s      → Start data collection
5s      → Data collection complete
        → Start GEO agent
10s     → GEO agent complete
        → Start DEMO agent
20s     → DEMO agent complete
        → Start COMP agent
30s     → COMP agent complete
        → Start TRANSIT agent
40s     → TRANSIT agent complete
        → Start RISK agent
50s     → RISK agent complete
        → Start REVENUE agent
60s     → REVENUE agent complete
        → Start ORCHESTRATOR
70s     → ORCHESTRATOR complete
        → Return response
```

**Response:**
```json
{
  "concept": "casual_dining",
  "sites": [
    {
      "address": "Mannerheimintie 1, Helsinki",
      "latitude": 60.1699,
      "longitude": 24.9384,
      "postal_code": "00100",
      "score": 87,
      "predicted_revenue_low": 95000,
      "predicted_revenue_mid": 145000,
      "predicted_revenue_high": 185000,
      "confidence": 89,
      "recommendation": "Highly Recommended",
      "strengths": [
        "High population density (8,900/km²)",
        "Median income €48k matches target market",
        "Excellent transit access"
      ],
      "risks": [
        "12 competitors in 1km radius"
      ],
      "features": {
        "population_1km": 28000,
        "population_density": 8900,
        "median_income": 48000,
        "competitors_count": 12,
        "nearest_metro_distance_m": 280,
        ...
      },
      "reasoning_summary": "🌟 Highly Recommended. This casual dining location scores 87/100 with 89% confidence. Predicted revenue: €145,000/month. Strong demographics and excellent transit access.",
      "agent_reasoning": {
        "geo": "Address successfully geocoded with high precision. Location validated in dense urban core of Helsinki. Data quality score: 95/100.",
        "demographics": "Demographics score 85/100. Population density 8,900/km² is optimal for casual dining. Median income €48,000 matches target range (€35k-€65k). Age distribution 68% working-age population provides strong target demographic.",
        "competition": "Competition score 72/100. 12 competitors within 1km indicates moderate saturation (4.2 per 1k residents). Nearest competitor 180m away provides manageable separation. Market gap: No dedicated vegan restaurants.",
        "transit": "Transit score 88/100. Tram stop 120m away provides excellent access. Metro station 280m ensures high connectivity. 45 walkability POIs indicate vibrant pedestrian area.",
        "risk": "Overall confidence 89%. High data quality with complete demographics, competition, and transit information. Risk level: Low. No major concerns identified.",
        "revenue": "Predicted monthly revenue €145,000 with realistic scenario. Key drivers: Demographics (35% weight, +€15k contribution), Transit (20% weight, +€10k contribution). Confidence: High based on 47 comparable openings."
      }
    }
  ],
  "ranking": null,
  "cannibalization_warning": null,
  "prediction_id": "pred_f8a9c2b1"
}
```

**Frontend:**
- Shows prediction card with score, revenue, recommendation
- Collapsible "Show Reasoning" section
- Full agent traces available

**Performance:**
- With agents: **60-90 seconds**
- Without agents (current): **10-15 seconds** (falls back to old scorer)

---

## Flow 4: Search Multiple Addresses → Comparison

**User Action:** Pastes 3 addresses (multiline):
```
Mannerheimintie 1, Helsinki
Hämeentie 5, Helsinki
Bulevardi 12, Helsinki
```

### Step 1: Detect Search Type

**Frontend:**
```typescript
const response = await fetch('/api/search', {
  method: 'POST',
  body: JSON.stringify({
    query: 'Mannerheimintie 1, Helsinki\nHämeentie 5, Helsinki\nBulevardi 12, Helsinki'
  })
});
```

**Backend:**
```python
def _detect_search_type(query: str) -> str:
    # Contains newlines
    if "\n" in query or ";" in query:
        return "multiple_addresses"

def _extract_addresses(query: str) -> List[str]:
    if "\n" in query:
        return [addr.strip() for addr in query.split("\n") if addr.strip()]
    elif ";" in query:
        return [addr.strip() for addr in query.split(";") if addr.strip()]
```

**Response:**
```json
{
  "search_type": "comparison",
  "city": null,
  "addresses": [
    "Mannerheimintie 1, Helsinki",
    "Hämeentie 5, Helsinki",
    "Bulevardi 12, Helsinki"
  ],
  "requires_concept": true
}
```

### Step 2: Analyze All Addresses

**Frontend:**
```typescript
const response = await fetch('/api/analyze', {
  method: 'POST',
  body: JSON.stringify({
    addresses: [
      'Mannerheimintie 1, Helsinki',
      'Hämeentie 5, Helsinki',
      'Bulevardi 12, Helsinki'
    ],
    concept: 'casual_dining'
  })
});
```

**Backend:**
- Processes each address sequentially (same as Flow 3)
- After all addresses analyzed, ranks by score
- Checks for cannibalization (if sites are <2km apart)

**Response:**
```json
{
  "concept": "casual_dining",
  "sites": [
    { ... site 1 data ... },
    { ... site 2 data ... },
    { ... site 3 data ... }
  ],
  "ranking": [0, 1, 2],  // Indices in score order (best → worst)
  "cannibalization_warning": "Sites 1 and 2 are 1.2km apart",
  "prediction_id": "pred_abc123"
}
```

**Frontend:**
- Renders ranked list (#1, #2, #3)
- Shows recommendation for each: "MAKE OFFER", "NEGOTIATE", "PASS"
- Highlights cannibalization warning if present

**Performance:**
- With agents: **3 × 70s = 3.5 minutes** (sequential)
- Without agents: **3 × 12s = 36 seconds**

---

## Flow 5: Submit Outcome (Future)

**User Action:** Opens restaurant, wants to report actual revenue

### Step 1: Navigate to Outcomes

**Frontend:**
```typescript
// From email link or saved prediction
navigate(`/outcomes?prediction_id=pred_abc123`);
```

### Step 2: Fetch Prediction

**Frontend:**
```typescript
const response = await fetch(`/api/predictions/${predictionId}`);
```

**Backend:**
```python
@app.get("/api/predictions/{prediction_id}")
async def get_prediction(prediction_id: str, db: Session = Depends(get_db)):
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id
    ).first()

    if not prediction:
        raise HTTPException(404, "Prediction not found")

    return {
        "prediction_id": prediction.id,
        "address": prediction.address,
        "predicted_revenue": prediction.predicted_revenue_mid,
        "predicted_range": {
            "low": prediction.predicted_revenue_low,
            "high": prediction.predicted_revenue_high
        },
        "concept": prediction.concept,
        "created_at": prediction.created_at
    }
```

### Step 3: Submit Outcome

**Frontend:**
```typescript
const response = await fetch('/api/outcomes', {
  method: 'POST',
  body: JSON.stringify({
    prediction_id: 'pred_abc123',
    actual_revenue: 152000,
    opening_date: '2025-03-15',
    notes: 'Exceeded expectations due to local events'
  })
});
```

**Backend:**
```python
@app.post("/api/outcomes")
async def submit_outcome(outcome: OutcomeSubmission, db: Session = Depends(get_db)):
    # 1. Fetch prediction
    prediction = db.query(Prediction).filter(
        Prediction.id == outcome.prediction_id
    ).first()

    # 2. Calculate variance
    predicted = prediction.predicted_revenue_mid
    actual = outcome.actual_revenue
    variance = ((actual - predicted) / predicted) * 100
    within_band = (
        prediction.predicted_revenue_low <= actual <= prediction.predicted_revenue_high
    )

    # 3. Store outcome
    outcome_record = Outcome(
        prediction_id=outcome.prediction_id,
        actual_revenue=outcome.actual_revenue,
        opening_date=outcome.opening_date,
        variance_percent=variance,
        within_predicted_band=within_band,
        notes=outcome.notes
    )
    db.add(outcome_record)
    db.commit()

    # 4. Update accuracy stats (aggregate)
    # ...

    return {
        "status": "recorded",
        "variance_percent": variance,
        "within_predicted_band": within_band,
        "message": "Thank you for helping improve our predictions!"
    }
```

**Frontend:**
- Shows success message
- Displays variance: "+4.8% vs predicted"
- Shows contribution to accuracy stats

---

## Flow 6: View Accuracy Stats

**User Action:** Clicks "See our accuracy" link

**Frontend:**
```typescript
const response = await fetch('/api/accuracy');
```

**Backend:**
```python
@app.get("/api/accuracy")
async def get_accuracy_stats(db: Session = Depends(get_db)):
    # Aggregate outcomes
    outcomes = db.query(Outcome).all()

    total_predictions = db.query(Prediction).count()
    sites_opened = len(outcomes)
    within_band = sum(1 for o in outcomes if o.within_predicted_band)
    avg_variance = sum(o.variance_percent for o in outcomes) / len(outcomes) if outcomes else 0

    return {
        "total_predictions": total_predictions,
        "sites_opened": sites_opened,
        "within_predicted_band": within_band,
        "accuracy_rate": within_band / sites_opened if sites_opened else 0,
        "avg_variance_percent": avg_variance
    }
```

**Response:**
```json
{
  "total_predictions": 1847,
  "sites_opened": 247,
  "within_predicted_band": 228,
  "accuracy_rate": 0.923,  // 92.3%
  "avg_variance_percent": 4.2  // On average, 4.2% higher than predicted
}
```

**Frontend:**
- Shows stats: "92.3% of predictions within range"
- Shows: "Average variance: +4.2%"
- Marketing message: "Based on 247 real openings"

---

## Error Handling

### Geocoding Failure
```python
geocode_result = await geocoder.geocode_address(address)
if not geocode_result:
    raise HTTPException(400, f"Could not find address: {address}")
```

### PAAVO Data Missing
```python
demographics = await statfin.get_demographics_by_postal_code(postal_code)
if not demographics:
    # Proceed without demographics (lower confidence)
    demographics = None
```

### Agent Failure (Future)
```python
try:
    analysis = await orchestrator.analyze_site(...)
except Exception as e:
    logger.error(f"Agno agents failed: {e}")
    # Fall back to old scorer
    analysis = scorer.calculate_score(features, concept)
    # Add warning to response
    warning = "Using basic scoring (AI agents unavailable)"
```

### Rate Limiting (Future)
```python
if user.requests_today > 100:
    raise HTTPException(429, "Rate limit exceeded. Upgrade to Scale tier.")
```

---

## Performance Summary

| Flow | Endpoint | Speed (Current) | Speed (With Agents) |
|------|----------|-----------------|---------------------|
| City search | `/api/discover` | 2s | 2s (no agents) |
| Postal code | `/api/discover` | 3-5s | 3-5s (no agents) |
| Single address | `/api/analyze` | 12s | **70s** |
| 3 addresses | `/api/analyze` | 36s | **210s** (3.5 min) |
| Submit outcome | `/api/outcomes` | <1s | <1s |
| View stats | `/api/accuracy` | <1s | <1s |

**Bottleneck:** Sequential OpenAI API calls for each agent (6 agents × 10s each = 60s per address)

**Optimization Options:**
1. Run agents in parallel (reduce to ~20s per address)
2. Cache common queries (second search for same address = instant)
3. Use streaming responses (show partial results as agents complete)
