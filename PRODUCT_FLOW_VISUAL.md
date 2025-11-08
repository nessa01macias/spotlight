# Spotlight Product Flow - Visual Guide

## 🎯 Complete User Journey with Trust Layer

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         1. LANDING PAGE (/)                              │
│                                                                          │
│  "Evidence-based site selection for Finland"                            │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  [Search Input]                                                 │    │
│  │   Helsinki or 00100_________________________ [🔍 Search]        │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  Try: Helsinki • 00100 • Mannerheimintie 1                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    POST /api/search (detect type)
                                    │
                ┌───────────────────┴────────────────────┐
                │                                        │
                ▼                                        ▼
┌─────────────────────────────────┐    ┌────────────────────────────────┐
│  City/Postal Code               │    │  Address                       │
│  → DISCOVERY FLOW               │    │  → ANALYSIS FLOW (future)      │
└─────────────────────────────────┘    └────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      2. DISCOVERY VIEW (/discover)                       │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ Helsinki                         Concept: [Casual Dining ✓]    │    │
│  ├────────────────────────────────────────────────────────────────┤    │
│  │                                                                 │    │
│  │  [MAP WITH HEATMAP]                                            │    │
│  │   • Red markers = High opportunity                             │    │
│  │   • Blue markers = Low opportunity                             │    │
│  │   • Confidence overlay on hover                                │    │
│  │                                                                 │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ #1  KAMPPI                                            54.4     │    │
│  │     Lat: 60.1699, Lng: 24.9342                                 │    │
│  │     Confidence: 82% • Coverage: 91%  ← NEW TRUST LAYER         │    │
│  │                                                                 │    │
│  │     Predicted Revenue: €935k - €1.27M                          │    │
│  │     Est. Rent: €42/sqft                                        │    │
│  │                                                                 │    │
│  │     [View Details →]  ← CLICKABLE!                             │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  (Repeat for #2 Kallio, #3 Pasila, etc.)                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
              Click tile → GET /api/area/{area_id}
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   3. AREA DETAIL VIEW (/area/[id])                       │
│                                                                          │
│  ┌─ [← Back to Discovery]                                              │
│  │                                                                       │
│  │  📍 KAMPPI                                            [54.4]         │
│  │  Helsinki                                                            │
│  │                                                                       │
│  │  ┌──────────────────────────────────────────────────────────────┐  │
│  │  │ 🎯 Confidence: 82% (High)  ← TRUST BADGE                     │  │
│  │  │                                                                │  │
│  │  │ Data Coverage:                     ← COVERAGE BAR             │  │
│  │  │ Demographics  ████████████████████  95%                       │  │
│  │  │ Competition   ███████████████       88%                       │  │
│  │  │ Transit       █████████████████     92%                       │  │
│  │  └──────────────────────────────────────────────────────────────┘  │
│  │                                                                       │
│  │  Predicted Annual Revenue                                            │
│  │  €13.2M   (€11.2M - €15.2M)                                         │
│  │  Confidence: 82%                                                     │
│  │                                                                       │
│  ├────────────────────────────────────────────────────────────────────│
│  │ Why This Area Scores 54/100          ← AUTO-GENERATED BULLETS      │
│  │                                                                       │
│  │  1. High population density: 28,000 people in 1km radius            │
│  │  2. Median income: €48,000/year matches target market               │
│  │  3. Excellent transit: Metro station 180m away                      │
│  │  4. Moderate competition: 12 competitors in area                    │
│  │                                                                       │
│  ├────────────────────────────────────────────────────────────────────│
│  │ Detailed Metrics                                                     │
│  │                                                                       │
│  │ ┌─────────────┬─────────────┬──────────────┐                       │
│  │ │Demographics │ Competition │ Transit      │                       │
│  │ │Population:  │ Competitors:│ Metro: 180m  │                       │
│  │ │ 28,000      │ 12          │ Tram: 120m   │                       │
│  │ │Income:      │ Per 1k: 0.4 │ POIs: 45     │                       │
│  │ │ €48,000/yr  │             │              │                       │
│  │ └─────────────┴─────────────┴──────────────┘                       │
│  │                                                                       │
│  ├────────────────────────────────────────────────────────────────────│
│  │ ✓ Key Strengths              ⚠ Key Risks                           │
│  │                                                                       │
│  │ • High foot traffic          • 12 competitors may dilute market     │
│  │ • Excellent transit access   • Premium rent (€42/sqft)             │
│  │ • Strong demographics                                                │
│  │                                                                       │
│  ├────────────────────────────────────────────────────────────────────│
│  │ How This Was Calculated      ← METHOD TRANSPARENCY                  │
│  │                                                                       │
│  │ Method: Heuristic Scoring                                            │
│  │ Data Sources:                                                        │
│  │  • Statistics Finland Population Grid (1km)                         │
│  │  • Statistics Finland PAAVO (Postal Code Demographics)              │
│  │  • OpenStreetMap (Competition Data)                                 │
│  │  • OpenStreetMap (Transit Data)                                     │
│  │                                                                       │
│  │ Confidence Basis: Based on data coverage and score component        │
│  │ consistency                                                          │
│  │                                                                       │
│  │ Last Updated: 2025-11-08T12:34:56Z                                  │
│  └─────────────────────────────────────────────────────────────────────│
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 API Flow Diagram

```
┌──────────┐
│  User    │
└────┬─────┘
     │
     │ 1. Types "Helsinki"
     ▼
┌─────────────────┐
│ POST /api/search│  Returns: { search_type: "discovery", city: "Helsinki" }
└────┬────────────┘
     │
     │ 2. Navigate to /discover
     ▼
┌──────────────────┐
│ POST /api/discover│  
└────┬─────────────┘  
     │
     │ Data Collection:
     │ • StatFin: Demographics (PAAVO)
     │ • PopGrid: Population density
     │ • OSM: Competition & transit
     │
     │ Trust Calculation:
     │ • Coverage: demographics=0.95, competition=0.88, transit=0.92
     │ • Confidence: 0.82 (based on coverage + consistency)
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ Returns: {                                              │
│   top_opportunities: [                                  │
│     {                                                   │
│       area_id: "helsinki_kamppi",                       │
│       score: 54.4,                                      │
│       confidence: 0.82,  ← TRUST METRIC                │
│       coverage: {        ← TRUST METRIC                │
│         demographics: 0.95,                             │
│         competition: 0.88,                              │
│         transit: 0.92,                                  │
│         overall: 0.91                                   │
│       }                                                 │
│     }                                                   │
│   ],                                                    │
│   method: {              ← TRANSPARENCY                 │
│     scoring_method: "heuristic",                        │
│     data_sources: [...],                                │
│     last_updated: "2025-11-08T12:34:56Z"               │
│   }                                                     │
│ }                                                       │
└─────────────────────────────────────────────────────────┘
     │
     │ 3. User clicks "Kamppi" tile
     ▼
┌─────────────────────────────────────────┐
│ GET /api/area/helsinki_kamppi           │
│     ?concept=CasualDining               │
└────┬────────────────────────────────────┘
     │
     │ Data Collection (same as above)
     │
     │ Additional Processing:
     │ • Generate "why" bullets (5 auto-generated)
     │ • Calculate strengths & risks
     │ • Method transparency info
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ Returns: {                                              │
│   area_id: "helsinki_kamppi",                           │
│   score: 54.4,                                          │
│   predicted_revenue_mid: 1100000,                       │
│   confidence: 0.82,                                     │
│   coverage: { ... },                                    │
│   method: { ... },                                      │
│   why: [                  ← AUTO-GENERATED BULLETS      │
│     "High population density: 28,000 in 1km",          │
│     "Median income: €48,000/year matches target",      │
│     "Excellent transit: Metro 180m away",              │
│     "Moderate competition: 12 competitors"             │
│   ],                                                    │
│   demographics: { ... },                                │
│   competition_analysis: { ... },                        │
│   traffic_access: { ... },                              │
│   strengths: [ ... ],                                   │
│   risks: [ ... ]                                        │
│ }                                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🎨 Trust Layer Visual Elements

### 1. Confidence Badge
```
┌─────────────────────────────────┐
│ 🎯 Confidence 82% (High)   [i] │  ← Emerald badge
└─────────────────────────────────┘

Colors:
• 0-60%:   🟡 Amber (Low)
• 60-75%:  🟢 Green (Medium)  
• 75-90%:  🟢 Emerald (High)
• 90-100%: 🟢 Dark Emerald (Very High)

Tooltip on hover:
┌────────────────────────────────────────┐
│ Confidence 82% — high data coverage    │
│ Based on population, income, transit,  │
│ competition. Data coverage: 91%.       │
└────────────────────────────────────────┘
```

### 2. Data Coverage Bar
```
Data Coverage                    91%

Demographics  ███████████████████  95%  (emerald)
Competition   ███████████████      88%  (blue)
Transit       █████████████████    92%  (purple)
```

### 3. Method Transparency Box
```
┌─────────────────────────────────────────────┐
│ How This Was Calculated                     │
│                                             │
│ Method: Heuristic Scoring                   │
│ Data Sources:                               │
│  • Statistics Finland Population Grid (1km) │
│  • Statistics Finland PAAVO (Postal Code)   │
│  • OpenStreetMap (Competition Data)         │
│  • OpenStreetMap (Transit Data)             │
│                                             │
│ Confidence Basis: Based on data coverage    │
│ and score component consistency             │
│                                             │
│ Last Updated: 2025-11-08T12:34:56Z         │
└─────────────────────────────────────────────┘
```

---

## 📊 Trust Metrics Calculation

### Coverage Calculation
```python
def calculate_coverage(features):
    # Count present fields in each category
    demographics = fields_present / total_fields
    competition = fields_present / total_fields
    transit = fields_present / total_fields
    
    # Weighted average
    overall = (
        demographics * 0.4 +
        competition * 0.3 +
        transit * 0.3
    )
    
    return {
        demographics: 0.95,  # 95% of demo fields present
        competition: 0.88,   # 88% of comp fields present
        transit: 0.92,       # 92% of transit fields present
        overall: 0.91        # Weighted average
    }
```

### Confidence Calculation
```python
def calculate_confidence(score_components, coverage):
    # Component 1: Data coverage (40%)
    coverage_score = coverage.overall * 0.4
    
    # Component 2: Score consistency (30%)
    # Lower variance = higher consistency
    consistency = 1 - (std_dev / 50)
    consistency_score = consistency * 0.3
    
    # Component 3: Feature completeness (30%)
    # All required fields present
    completeness = present / required
    completeness_score = completeness * 0.3
    
    # Total
    confidence = coverage_score + consistency_score + completeness_score
    
    return 0.82  # 82% confidence
```

### "Why" Bullet Generation
```python
def generate_why_bullets(features, score_components):
    bullets = []
    
    # Population
    if pop > 20000:
        bullets.append(f"High population density: {pop:,} in 1km")
    
    # Income
    if income > 50000:
        bullets.append(f"High median income: €{income:,}/year")
    
    # Transit
    if metro_dist < 300:
        bullets.append(f"Excellent transit: Metro {metro_dist}m away")
    
    # Competition
    if comp_count < 5:
        bullets.append(f"Low competition: Only {comp_count} competitors")
    
    return bullets[:5]  # Max 5 bullets
```

---

## 🚀 Key Features

### ✅ Implemented
- [x] Trust metrics calculate confidence (0-1) and coverage (per source)
- [x] Discovery tiles show inline confidence and coverage percentages
- [x] Area detail page shows full trust breakdown
- [x] Confidence badge with color coding (amber/green/emerald)
- [x] Data coverage bar (3 segments for 3 data sources)
- [x] Auto-generated "why" bullets explaining the score
- [x] Method transparency showing how calculated and data sources
- [x] Clickable flow: discovery → area detail
- [x] Works for both cities and postal codes

### 🎯 Impact
**Before:** "Looks like fake information" - No trust indicators
**After:** "Reads like a professional tool" - Full transparency

**Trust layer wired end-to-end. Every prediction now comes with confidence, coverage, and method info.**

