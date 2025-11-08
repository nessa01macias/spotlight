# Routing Logic & Decision Trees

This document explains the **decision logic** behind Spotlight's routing and processing choices. It answers "when to route where" and "when to use which processing mode".

---

## 1. Input Detection & Routing

### Entry Point: Landing Page Search

When a user enters text into the landing page search:

```
User Input → Detection Algorithm → Route to Discovery OR Analysis
```

### Detection Algorithm

```python
def detect_input_type(user_input: str) -> str:
    """
    Detect whether user input is:
    - City name → Discovery
    - Postal code → Discovery
    - Single address → Analysis
    - Multiple addresses → Analysis (Comparison mode)
    """

    # Step 1: Check for multiple lines (address comparison)
    lines = user_input.strip().split('\n')
    if len(lines) >= 2:
        # Check if each line looks like an address
        if all(is_likely_address(line) for line in lines):
            return "ANALYSIS_COMPARISON"

    # Step 2: Check for postal code (5 digits)
    if re.match(r'^\d{5}$', user_input.strip()):
        return "DISCOVERY_POSTAL"

    # Step 3: Check for street address (contains number + street name)
    if re.search(r'\d+.*[a-zA-Z]+', user_input):
        # Has numbers and letters → likely address
        return "ANALYSIS_SINGLE"

    # Step 4: Default to city search
    return "DISCOVERY_CITY"

def is_likely_address(text: str) -> bool:
    """Check if text looks like a street address"""
    # Contains both numbers and letters
    has_number = bool(re.search(r'\d', text))
    has_letters = bool(re.search(r'[a-zA-Z]', text))
    return has_number and has_letters
```

### Routing Table

| User Input | Detected Type | Route To | Example |
|------------|---------------|----------|---------|
| "Helsinki" | DISCOVERY_CITY | `/api/discover` | City exploration |
| "00100" | DISCOVERY_POSTAL | `/api/discover` | Postal code heatmap |
| "Mannerheimintie 1, Helsinki" | ANALYSIS_SINGLE | `/api/analyze` | Single address analysis |
| "Addr1\nAddr2\nAddr3" | ANALYSIS_COMPARISON | `/api/analyze` (batch) | Compare 3 addresses |

---

## 2. Processing Mode Selection

### Discovery Mode (Fast Pre-Scoring)

**When to Use:**
- City-wide exploration
- Postal code area analysis
- Need results in <3 seconds
- Showing 10-50+ locations on heatmap

**Processing:**
```
User Input → Geocoding → Population Grid → Pre-Scoring (Deterministic) → Heatmap
```

**Algorithm:**
```python
# Old ScoringEngine (fast, deterministic)
def pre_score_location(lat, lng, concept):
    """
    Quick scoring for heatmap display
    Time: <100ms per location
    """

    # 1. Population density (30%)
    pop_score = calculate_population_score(lat, lng, radius=1km)

    # 2. Competition proximity (25%)
    comp_score = calculate_competition_score(lat, lng, concept)

    # 3. Transit access (25%)
    transit_score = calculate_transit_score(lat, lng)

    # 4. Walkability (20%)
    walk_score = calculate_walkability_score(lat, lng)

    # Weighted score
    return (pop_score * 0.30 +
            comp_score * 0.25 +
            transit_score * 0.25 +
            walk_score * 0.20)
```

**Why Fast:**
- No AI agent reasoning
- Simple heuristics
- Cached data sources
- Parallel processing

**Trade-off:**
- Less nuanced
- No reasoning transparency
- Generic concept mapping

---

### Analysis Mode (Deep AI Reasoning)

**When to Use:**
- Evaluating specific address(es)
- Making investment decision
- Need transparent reasoning
- User willing to wait 60-90 seconds

**Processing:**
```
Address → Data Collection → 6 Agno Agents → Orchestrator Synthesis → Prediction
```

**Agent Execution Timeline:**

```
0-10s:   Data Collection (parallel)
         ├─ Geocoding (Digitransit)
         ├─ Demographics (PAAVO)
         ├─ Competition (Overpass)
         └─ Transit (Digitransit)

10-20s:  GEO Agent
         └─ Validate location quality

20-30s:  DEMO Agent
         └─ Analyze target demographics

30-40s:  COMP Agent
         └─ Analyze competition landscape

40-50s:  TRANSIT Agent
         └─ Assess accessibility

50-60s:  RISK Agent
         └─ Calculate confidence & risk

60-70s:  REVENUE Agent
         └─ Predict revenue

70-80s:  ORCHESTRATOR
         └─ Synthesize final recommendation

Total: 70-80 seconds
```

**Why Slow:**
- 6 AI agents with reasoning enabled
- Chain-of-thought processing
- Comprehensive analysis
- Transparent explanations

**Trade-off:**
- High latency (60-90s)
- Higher cost per prediction
- Requires OpenAI API

**Value:**
- Nuanced, context-aware predictions
- Transparent reasoning traces
- Concept-specific insights
- Investment-grade confidence

---

## 3. Agent Activation Logic

### When to Enable Agno Agents

```python
def should_use_agents(request_type: str, user_tier: str) -> bool:
    """
    Decide whether to use expensive Agno agents or fast pre-scoring
    """

    # Always use agents for Analysis mode
    if request_type in ["ANALYSIS_SINGLE", "ANALYSIS_COMPARISON"]:
        return True

    # Discovery mode: depends on user tier
    if request_type in ["DISCOVERY_CITY", "DISCOVERY_POSTAL"]:
        # Pro users can enable "Deep Discovery"
        if user_tier == "pro" and request.deep_analysis:
            return True
        else:
            return False  # Use fast pre-scoring

    return False
```

### Agent Selection Logic

Not all agents run for all requests:

| Request Type | Agents Used | Why |
|-------------|-------------|-----|
| Single Address Analysis | ALL (GEO, DEMO, COMP, TRANSIT, RISK, REVENUE) | Full context needed |
| Address Comparison (2-3) | ALL (run for each address) | Compare apples-to-apples |
| Address Comparison (4+) | GEO, DEMO, COMP only | Performance limit |
| Discovery (if enabled) | DEMO, COMP, TRANSIT only | Skip GEO/RISK (not address-specific) |

**Code:**
```python
def select_agents(request_type: str, address_count: int) -> List[str]:
    """Select which agents to run"""

    if request_type == "ANALYSIS_SINGLE":
        return ["GEO", "DEMO", "COMP", "TRANSIT", "RISK", "REVENUE"]

    elif request_type == "ANALYSIS_COMPARISON":
        if address_count <= 3:
            return ["GEO", "DEMO", "COMP", "TRANSIT", "RISK", "REVENUE"]
        else:
            # Too many addresses → skip expensive agents
            return ["GEO", "DEMO", "COMP"]

    elif request_type == "DISCOVERY":
        # No address-specific agents
        return ["DEMO", "COMP", "TRANSIT"]

    return []
```

---

## 4. Caching Strategy

### What to Cache

| Data Type | Cache Duration | Why |
|-----------|----------------|-----|
| PAAVO Demographics | 30 days | Updated annually |
| Population Grid | 30 days | Updated annually |
| Geocoding Results | 90 days | Addresses don't change |
| Competition Data | 7 days | Businesses open/close |
| Transit Stops | 30 days | Routes change occasionally |
| Walkability POIs | 14 days | POIs change moderately |

### When to Bypass Cache

```python
def should_bypass_cache(request) -> bool:
    """
    Decide whether to bypass cache and fetch fresh data
    """

    # User explicitly requested fresh data
    if request.force_refresh:
        return True

    # High-value decision (pro tier)
    if request.user_tier == "pro" and request.importance == "high":
        return True

    # Outcome tracking submission (need fresh baseline)
    if request.is_outcome_tracking:
        return True

    return False
```

---

## 5. Error Handling & Fallbacks

### Geocoding Failures

```
User Input → Digitransit Geocode
                ↓ (if fails)
            Fallback to Nominatim
                ↓ (if fails)
            Return "Unable to locate address" error
```

### Missing Demographics

```
Address → Extract Postal Code → PAAVO API
                                    ↓ (if fails)
                                Fallback to Population Grid (1km)
                                    ↓ (if fails)
                                Use city-wide averages
```

### Agent Failures

```
Agent Execution → Agent Timeout (30s)
                    ↓ (if fails)
                Fall back to deterministic scoring
                    ↓
                Flag low confidence
```

**Code:**
```python
async def run_agent_with_fallback(agent, *args, **kwargs):
    """Run agent with timeout and fallback"""
    try:
        result = await asyncio.wait_for(
            agent.run(*args, **kwargs),
            timeout=30  # 30-second timeout per agent
        )
        return result

    except asyncio.TimeoutError:
        logger.error(f"{agent.name} timed out")
        return fallback_deterministic_score(*args, **kwargs)

    except Exception as e:
        logger.error(f"{agent.name} failed: {e}")
        return fallback_deterministic_score(*args, **kwargs)
```

---

## 6. Confidence-Based Routing

### Low Confidence → Request More Data

If confidence score < 60%:

```python
def handle_low_confidence(prediction):
    """
    When confidence is low, guide user to provide more context
    """

    missing_data = prediction.risk_assessment["missing_data"]

    # Suggest next steps
    suggestions = []

    if "demographics" in missing_data:
        suggestions.append({
            "action": "specify_target_customer",
            "message": "Tell us more about your target customer (age, income, lifestyle)"
        })

    if "concept_details" in missing_data:
        suggestions.append({
            "action": "provide_concept",
            "message": "Share your concept (casual dining, fine dining, quick service)"
        })

    if "local_context" in missing_data:
        suggestions.append({
            "action": "on_site_visit",
            "message": "Schedule on-site visit to assess foot traffic and visibility"
        })

    return {
        "confidence": prediction.confidence,
        "warning": "Low confidence prediction",
        "suggestions": suggestions
    }
```

---

## 7. Recommendation Mapping

### Score + Confidence → Actionable Recommendation

```python
def map_to_recommendation(score: int, confidence: int) -> Dict:
    """
    Map numeric scores to actionable recommendations
    """

    # High confidence tier
    if confidence >= 80:
        if score >= 85:
            return {
                "label": "🌟 Highly Recommended",
                "action": "MAKE OFFER",
                "color": "green",
                "reasoning": "Strong fundamentals with high confidence"
            }
        elif score >= 70:
            return {
                "label": "✅ Recommended",
                "action": "MAKE OFFER",
                "color": "green",
                "reasoning": "Good opportunity with reliable data"
            }
        elif score >= 55:
            return {
                "label": "⚠️ Consider Alternatives",
                "action": "NEGOTIATE",
                "color": "yellow",
                "reasoning": "Moderate potential, negotiate terms"
            }
        else:
            return {
                "label": "❌ Not Recommended",
                "action": "PASS",
                "color": "red",
                "reasoning": "High risk of underperformance"
            }

    # Medium confidence tier (65-79%)
    elif confidence >= 65:
        if score >= 75:
            return {
                "label": "✅ Recommended (Verify)",
                "action": "MAKE OFFER",
                "color": "green",
                "reasoning": "Good opportunity, recommend site visit"
            }
        elif score >= 60:
            return {
                "label": "⚠️ Conditional",
                "action": "NEGOTIATE",
                "color": "yellow",
                "reasoning": "Moderate data, needs validation"
            }
        else:
            return {
                "label": "❌ High Risk",
                "action": "PASS",
                "color": "red",
                "reasoning": "Limited data suggests avoiding"
            }

    # Low confidence (<65%)
    else:
        return {
            "label": "❓ Insufficient Data",
            "action": "RESEARCH",
            "color": "gray",
            "reasoning": "Collect more data before deciding"
        }
```

---

## 8. Multi-Address Comparison Logic

### When Comparing 2-3 Addresses

```python
def compare_addresses(predictions: List[Prediction]) -> Dict:
    """
    Compare multiple addresses and rank them
    """

    # Sort by combined score (score * confidence)
    ranked = sorted(
        predictions,
        key=lambda p: p.opportunity_score * (p.confidence / 100),
        reverse=True
    )

    # Identify winner
    winner = ranked[0]

    # Calculate relative scores
    for i, pred in enumerate(ranked):
        pred.rank = i + 1
        pred.relative_score = (pred.opportunity_score / winner.opportunity_score) * 100

    # Generate comparison insights
    insights = []

    # Best transit access
    best_transit = max(predictions, key=lambda p: p.transit_score)
    insights.append(f"{best_transit.address} has best transit access")

    # Best demographics
    best_demo = max(predictions, key=lambda p: p.demographic_score)
    insights.append(f"{best_demo.address} has strongest demographics")

    # Lowest competition
    lowest_comp = min(predictions, key=lambda p: p.competition_density)
    insights.append(f"{lowest_comp.address} has least competition")

    return {
        "ranked_predictions": ranked,
        "winner": winner,
        "insights": insights,
        "recommendation": f"Prioritize {winner.address} for lease negotiation"
    }
```

---

## 9. Future: Outcome Learning Routing

### When Actual Revenue Data Exists

```python
def enhance_prediction_with_outcomes(prediction: Prediction) -> Prediction:
    """
    If we have similar site outcomes, use them to calibrate prediction
    """

    # Find similar sites with known outcomes
    similar_sites = db.query(Outcome).filter(
        Outcome.concept == prediction.concept,
        Outcome.city == prediction.city,
        Outcome.confidence >= 70
    ).limit(10)

    if similar_sites:
        # Calculate actual vs predicted accuracy
        accuracy = calculate_accuracy(similar_sites)

        # Adjust current prediction
        calibrated_revenue = prediction.predicted_revenue * accuracy.correction_factor

        # Increase confidence
        calibrated_confidence = min(prediction.confidence + 10, 95)

        prediction.predicted_revenue = calibrated_revenue
        prediction.confidence = calibrated_confidence
        prediction.calibration_note = f"Adjusted based on {len(similar_sites)} similar sites"

    return prediction
```

**The Moat:** Over time, predictions become more accurate because we learn from outcomes.

---

## 10. Performance Optimization Rules

### When to Run in Parallel

```python
# ✅ GOOD: Independent data sources
async def collect_data_parallel(address):
    results = await asyncio.gather(
        geocode_address(address),      # Independent
        fetch_demographics(postal_code),  # Independent
        fetch_competition(lat, lng),   # Independent
        fetch_transit(lat, lng)        # Independent
    )
    return results

# ❌ BAD: Sequential dependencies
async def run_agents_sequential(data):
    geo = await geo_agent.run(data)
    demo = await demo_agent.run(data)  # Could run in parallel with geo
    comp = await comp_agent.run(data)  # Could run in parallel
    # ... but orchestrator needs all results first
```

### Current Limitations

| Operation | Max Parallelism | Why |
|-----------|-----------------|-----|
| Data Collection | 4 sources | API rate limits |
| Agent Execution | 1 at a time | Sequential reasoning dependency |
| Address Comparison | 3 addresses | Performance/cost balance |
| Discovery Pre-Scoring | 50 locations | Memory limits |

### Future Optimizations

1. **Parallel Agent Execution**: Run DEMO, COMP, TRANSIT in parallel (they don't depend on each other)
2. **Streaming Results**: Show partial results as agents complete
3. **Pre-computed Heatmaps**: Cache city-wide pre-scores
4. **Edge Caching**: CDN for static demographic data

---

## Summary: Decision Tree

```
User Input
    │
    ├─ Multiple Addresses? → Analysis (Comparison)
    ├─ Single Address? → Analysis (Single)
    ├─ Postal Code? → Discovery
    └─ City Name? → Discovery

Discovery
    │
    ├─ Pro User + Deep Analysis? → Use Agents (slow)
    └─ Default → Pre-Scoring (fast)

Analysis
    │
    ├─ 1-3 Addresses? → ALL agents
    └─ 4+ Addresses? → Partial agents

Agent Execution
    │
    ├─ All agents succeed? → High confidence
    ├─ Some agents fail? → Fallback scoring
    └─ All agents fail? → Error message

Recommendation
    │
    ├─ Score + Confidence → Map to action
    └─ Low Confidence → Request more data
```

---

**This routing logic ensures:**
- Fast performance for exploration (Discovery)
- Deep analysis for decision-making (Analysis)
- Graceful degradation when data is missing
- Cost optimization (agents only when needed)
- Clear user guidance at every step