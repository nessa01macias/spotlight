# Spotlight Product Flow Map

**Complete view hierarchy and navigation**

## View Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       LANDING PAGE (/)                          │
│                                                                 │
│  "Evidence-based site selection for Finland"                   │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ [Search Input]                                          │   │
│  │  helsinki______________________________________  [🔍]   │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Try: [Helsinki] [00100] [Kamppi 5]                           │
│                                                                 │
│  Input Detection Logic:                                        │
│  ├─ "Helsinki" → City search → Discovery Flow                 │
│  ├─ "00100" → Postal code → Discovery Flow                    │
│  ├─ "Mannerheimintie 1, Helsinki" → Address → Analysis Flow   │
│  └─ "Addr1\nAddr2\nAddr3" → Multiple → Comparison Flow        │
└─────────────────────────────────────────────────────────────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
    ┌────────────────────┐    ┌────────────────────────┐
    │  DISCOVERY VIEW    │    │   ANALYSIS VIEW        │
    │  (/discover)       │    │   (/analyze)           │
    └────────────────────┘    └────────────────────────┘
```

---

## 1. Landing Page (`/`)

### Purpose
Single entry point for all Spotlight searches. Intelligently routes to appropriate view based on input type.

### User Sees
- Large search input (center of page)
- Tagline: "Evidence-based site selection for Finland"
- Example searches: "Helsinki", "00100", "Kamppi 5"
- (Future) Quick stats: "Analyzed 1,847 locations for 127 restaurant chains"

### User Actions
1. Types query in search box
2. Presses Enter or clicks search icon

### Behind the Scenes
**Frontend:**
```typescript
POST /api/search
{
  "query": "helsinki"  // or address, or postal code
}
```

**Backend Response:**
```json
{
  "search_type": "discovery",  // or "single_site" or "comparison"
  "city": "Helsinki",          // if city/postal
  "addresses": null,           // if addresses
  "requires_concept": true     // Always true (user must select concept)
}
```

**Frontend Routing:**
- If `search_type === "discovery"` → Navigate to `/discover`
- If `search_type === "single_site"` → Navigate to `/analyze`
- If `search_type === "comparison"` → Navigate to `/analyze`

### Input Detection Logic

**City Name** (e.g., "Helsinki", "Tampere")
- Pattern: 1-2 words, no numbers
- Detection: `len(words) <= 2 && !containsNumbers`
- Route: Discovery View

**Postal Code** (e.g., "00100", "33100")
- Pattern: Exactly 5 digits
- Detection: `regex: ^\d{5}$`
- Route: Discovery View (shows single area)

**Single Address** (e.g., "Mannerheimintie 1, Helsinki")
- Pattern: Contains numbers + street name
- Detection: `regex: \d+\s+[A-Za-zäöåÄÖÅ]+`
- Route: Analysis View

**Multiple Addresses** (e.g., "Addr1\nAddr2\nAddr3")
- Pattern: Newlines or semicolons
- Detection: `query.includes('\n') || query.includes(';')`
- Route: Analysis View (comparison mode)

---

## 2. Discovery View (`/discover`)

### Purpose
City-wide or area-wide exploration. Shows heatmap of opportunities across a region.

### URL Pattern
```
/discover?city=Helsinki&concept=casual_dining
/discover?city=00100&concept=casual_dining  (postal code)
```

### User Sees

**Top Section:**
```
┌─────────────────────────────────────────────────────┐
│ ← Back to Search          📍 helsinki               │
├─────────────────────────────────────────────────────┤
│ Select Restaurant Concept                           │
│ [Quick Service] [Fast Casual] [Coffee Shop]         │
│ [Casual Dining ✓] [Fine Dining]                     │
└─────────────────────────────────────────────────────┘
```

**Main Content:**
```
┌─────────────────────────────────────────────────────┐
│ Areas Analyzed: 8              Concept: Casual Dining│
├─────────────────────────────────────────────────────┤
│                                                      │
│  [MAP WITH HEATMAP]                                 │
│  Red markers = High opportunity                     │
│  Blue markers = Low opportunity                     │
│                                                      │
├─────────────────────────────────────────────────────┤
│ Top Opportunities                                   │
│                                                      │
│ #1 Kamppi                              54.4         │
│    Lat: 60.1699, Lng: 24.9342                      │
│    Predicted Revenue: €935k - €1.27M                │
│    Est. Rent: €42/sqft                              │
│                                                      │
│ #2 Töölö                               50.1         │
│    ...                                              │
└─────────────────────────────────────────────────────┘
```

### User Actions
1. **Change Concept** → Re-runs scoring for new concept
2. **Click Area Card** (Future) → Navigate to detailed analysis of that area
3. **Zoom/Pan Map** → Visual exploration

### Behind the Scenes

**API Call:**
```typescript
POST /api/discover
{
  "city": "Helsinki",  // or postal code "00100"
  "concept": "casual_dining"
}
```

**Backend Processing:**
1. Detects if input is postal code (5 digits)
   - If postal code → `_analyze_postal_area()` (single area)
   - If city → Load pre-defined areas
2. For each area:
   - Fetch demographics (PAAVO)
   - Fetch population grid (Statistics Finland)
   - Fetch competition (OSM)
   - Fetch transit (Digitransit)
3. **Uses old ScoringEngine** (deterministic heuristics, NO agents)
   - Fast (<2 seconds for 8 areas)
   - No reasoning traces
4. Returns heatmap data + top 10 list

**Response:**
```json
{
  "city": "Helsinki",
  "concept": "casual_dining",
  "heatmap_data": [
    {"latitude": 60.1699, "longitude": 24.9342, "score": 54.4, "weight": 0.544},
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

### Current Limitations
- Only 8 hardcoded areas for Helsinki
- Uses old scorer (not Agno agents)
- No reasoning traces
- Can't click area to see details

### Future Enhancements
- Generate grid dynamically (50-100 areas)
- Use Agno agents for pre-scoring (overnight batch job)
- Click area → Detailed analysis view
- Filter by score/rent/properties
- Save favorite areas

---

## 3. Analysis View (`/analyze`)

### Purpose
Deep analysis of specific address(es). Uses Agno reasoning agents for transparent predictions.

### URL Pattern
```
/analyze?addresses=Mannerheimintie+1,Helsinki&concept=casual_dining
/analyze?addresses=Addr1;Addr2;Addr3&concept=casual_dining  (comparison)
```

### User Sees

**Single Address:**
```
┌─────────────────────────────────────────────────────┐
│ Mannerheimintie 1, Helsinki                        │
│ Score: 87/100                           ⭐ Highly    │
│                                         Recommended  │
├─────────────────────────────────────────────────────┤
│ Predicted Revenue (Year 1)                         │
│ €145,000/month                                     │
│ Range: €95k - €185k                                │
│ Confidence: 89%                                     │
├─────────────────────────────────────────────────────┤
│ Key Strengths                                       │
│ ✓ High population density (8,900/km²)              │
│ ✓ Median income €48k matches target market         │
│ ✓ Excellent transit access                         │
├─────────────────────────────────────────────────────┤
│ Key Concerns                                        │
│ ⚠ 12 competitors in 1km radius                     │
├─────────────────────────────────────────────────────┤
│ [Show Full Reasoning ↓]                            │
│                                                      │
│ (Expandable section with agent traces)              │
│ GEO Agent: High confidence location validation...   │
│ DEMO Agent: Demographics score 85/100...            │
│ COMP Agent: Moderate competition...                 │
│ ...                                                  │
└─────────────────────────────────────────────────────┘
```

**Multiple Addresses (Comparison):**
```
┌─────────────────────────────────────────────────────┐
│ Comparison Results - Ranked by Opportunity          │
├─────────────────────────────────────────────────────┤
│ #1 ✅ Mannerheimintie 1, Helsinki          87      │
│    Recommendation: MAKE OFFER                        │
│    Revenue: €145k/mo (€95k - €185k)                │
│    [Show Reasoning ↓]                               │
├─────────────────────────────────────────────────────┤
│ #2 ⚠️ Hämeentie 5, Helsinki                72      │
│    Recommendation: NEGOTIATE                         │
│    Revenue: €120k/mo (€80k - €160k)                │
│    [Show Reasoning ↓]                               │
├─────────────────────────────────────────────────────┤
│ #3 ❌ Bulevardi 12, Helsinki               55      │
│    Recommendation: PASS                              │
│    Revenue: €95k/mo (€65k - €125k)                 │
│    [Show Reasoning ↓]                               │
└─────────────────────────────────────────────────────┘
```

### User Actions
1. **Expand "Show Reasoning"** → See full agent analysis
2. **Export to PDF** (Future)
3. **Share Results** (Future)
4. **Submit Outcome** (Future) → Track actual revenue

### Behind the Scenes

**API Call:**
```typescript
POST /api/analyze
{
  "addresses": [
    "Mannerheimintie 1, Helsinki",
    "Hämeentie 5, Helsinki",
    "Bulevardi 12, Helsinki"
  ],
  "concept": "casual_dining"
}
```

**Backend Processing:**

For EACH address:

**Phase 1: Data Collection** (5-10 seconds)
```
DataCollector.collect_site_data():
├─ Digitransit: Geocode address → lat/lng/postal_code
├─ PAAVO: Get demographics for postal code
├─ Population Grid: Get density in 1km radius
├─ OSM: Get competitors, transit stops, POIs
└─ Returns: Complete feature set
```

**Phase 2: Agno Agent Analysis** (30-60 seconds)
```
OrchestratorAgent.analyze_site():
│
├─ 1. GEO Agent
│    Input: Address, geocoding result
│    Output: Confidence (high/medium/low), geographic context
│    Reasoning: "Address successfully geocoded with high precision..."
│
├─ 2. DEMO Agent
│    Input: Demographics data, concept
│    Output: Demographic score (0-100), income fit, age fit
│    Reasoning: "Median income €48k matches casual dining target..."
│
├─ 3. COMP Agent
│    Input: Competitor list, population
│    Output: Competition score (0-100), saturation level, market gaps
│    Reasoning: "12 competitors indicates moderate saturation..."
│
├─ 4. TRANSIT Agent
│    Input: Transit data, walkability POIs
│    Output: Transit score (0-100), accessibility rating
│    Reasoning: "Tram stop 120m away provides excellent access..."
│
├─ 5. RISK Agent
│    Input: All previous agent results
│    Output: Overall confidence (0-100), risk level, missing data
│    Reasoning: "High confidence prediction based on complete data..."
│
├─ 6. REVENUE Agent
│    Input: All agent scores
│    Output: Revenue prediction, opportunity score, key drivers
│    Reasoning: "Predicted €145k/month based on demographics (35% weight)..."
│
└─ 7. ORCHESTRATOR
     Input: All agent outputs
     Output: Final recommendation, executive summary
     Reasoning: "Highly Recommended. Strong demographics, moderate competition..."
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
      "reasoning_summary": "🌟 Highly Recommended. This casual dining location scores 87/100...",
      "agent_reasoning": {
        "geo": "Address successfully geocoded...",
        "demographics": "Demographics score 85/100...",
        "competition": "Competition score 72/100...",
        "transit": "Transit score 88/100...",
        "risk": "Overall confidence 89%...",
        "revenue": "Predicted revenue €145k/month..."
      }
    }
  ],
  "ranking": [0, 1, 2],  // If multiple addresses
  "prediction_id": "pred_abc123"
}
```

### Performance
- Single address: **30-90 seconds**
- Multiple addresses: Sequential (not parallel), **60-180 seconds for 3 addresses**
- **Bottleneck:** OpenAI API calls for each agent

### Current Limitations
- **Agents are commented out** (code references orchestrator but it's not initialized)
- Falls back to old scorer (if agents not enabled)
- Sequential processing (slow for multiple addresses)

### Future Enhancements
- Parallel agent execution (faster)
- Cache common analyses
- Add PDF export
- Add outcome submission
- Show comparison matrix for multiple sites

---

## 4. (Future) Outcome Tracking View

### Purpose
Submit actual revenue after restaurant opening. Builds "the moat" through outcome learning.

### URL Pattern
```
/outcomes?prediction_id=pred_abc123
```

### User Sees
```
┌─────────────────────────────────────────────────────┐
│ Submit Opening Outcome                              │
│                                                      │
│ Prediction for: Mannerheimintie 1, Helsinki        │
│ Predicted Revenue: €145k/month                      │
│ Predicted Range: €95k - €185k                       │
│                                                      │
│ Actual Performance:                                  │
│ Opening Date: [2025-03-15]                          │
│ Actual Monthly Revenue: [€ _______]                 │
│                                                      │
│ Notes (optional):                                    │
│ [Exceeded expectations due to...]                   │
│                                                      │
│ [Submit Outcome]                                     │
└─────────────────────────────────────────────────────┘
```

### Behind the Scenes
**API Call:**
```typescript
POST /api/outcomes
{
  "prediction_id": "pred_abc123",
  "actual_revenue": 152000,
  "opening_date": "2025-03-15",
  "notes": "Exceeded expectations"
}
```

**Backend:**
1. Fetch prediction from database
2. Calculate variance: `(actual - predicted) / predicted`
3. Store outcome in `Outcome` table
4. Update accuracy stats

**Response:**
```json
{
  "status": "recorded",
  "variance_percent": 4.8,  // 4.8% higher than predicted
  "within_predicted_band": true,  // €152k is within €95k-€185k
  "message": "Thank you! This outcome helps improve predictions."
}
```

### Future Impact
- Every outcome trains the model
- Improves prediction accuracy over time
- **THE MOAT:** Competitors can't access this data

---

## Navigation Summary

```
Landing → Discovery → (Future) Area Detail
        ↓
        Analysis → (Future) Outcome Tracking
```

**Primary Flow (Current):**
1. User searches city/postal code → Discovery view
2. User searches address(es) → Analysis view

**Future Flow:**
1. User searches city → Discovery view
2. User clicks area → Area detail view (pre-scored)
3. User clicks "Analyze specific address" → Analysis view (on-demand agents)
4. User opens restaurant → Outcome tracking
5. System learns → Improves predictions

---

## Technical Endpoints

| Endpoint | Purpose | Uses Agents? | Speed |
|----------|---------|--------------|-------|
| `POST /api/search` | Detect input type | No | Instant |
| `POST /api/discover` | City/area discovery | No (old scorer) | <2s |
| `POST /api/analyze` | Address analysis | **Should use** (currently disabled) | 30-90s |
| `POST /api/outcomes` | Submit actual revenue | No | Instant |
| `GET /api/accuracy` | Get accuracy stats | No | Instant |

---

## Decision Points to Resolve

1. **Should discovery use Agno agents?**
   - **Pro:** Smarter predictions, reasoning traces
   - **Con:** Slower (30s per area × 8 areas = 4 minutes)
   - **Option:** Pre-score with agents overnight, serve fast

2. **Should landing page prioritize address input?**
   - **Pro:** Matches business model ("paste 3 addresses")
   - **Con:** Loses exploration capability
   - **Option:** Dual entry points (quick address input + explore link)

3. **Should we keep discovery view?**
   - **Pro:** Useful for exploration
   - **Con:** Not core use case ("evaluate broker proposals")
   - **Option:** Keep but deprioritize (smaller in UI)

4. **Should we show reasoning by default?**
   - **Pro:** Transparency builds trust
   - **Con:** Overwhelming for quick decisions
   - **Option:** Summary by default, "Show details" to expand
