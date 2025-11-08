# Provenance Display Implementation

## Overview
Added transparent provenance tracking and display to show users **why** each rating was calculated and **where** the data comes from. This aligns with the provenance-first approach.

## Backend Changes

### 1. Enhanced Data Model ([backend/models/schemas.py](backend/models/schemas.py))

Added new schemas:
- **`MetricProvenance`**: Tracks individual metric contributions
  - `score`: Component score (0-100)
  - `weight`: Weight in overall calculation (0-1)
  - `weighted_score`: Actual contribution to final score
  - `source`: Data source name (e.g., "Statistics Finland")
  - `coverage`: Data quality (0-1)
  - `raw_value` & `raw_unit`: Original data (e.g., "27000 people")

- **`ScoreProvenance`**: Complete score breakdown
  - Per-metric provenance for all components
  - `total_score`: Final calculated score
  - `confidence_basis`: Explanation of confidence calculation

- **Updated `RecommendedAddress`**:
  - Added `decision_reasoning`: Human-readable decision explanation
  - Added `provenance`: Complete score breakdown with sources

### 2. Score Calculation ([backend/services/address_generator.py](backend/services/address_generator.py))

Updated `_score_candidate()` method:
- Tracks individual component scores separately
- Builds detailed provenance object with:
  - Population: "Statistics Finland Population Grid 2023"
  - Transit: "Digitransit Finland API"
  - Competition: "OpenStreetMap Overpass API"
  - Income: "PAAVO Postal Demographics (placeholder)"
  - Traffic: "Traffic model (placeholder)"

- Generates decision reasoning:
  - **MAKE_OFFER**: "Strong site: score 87.3/100 (target ≥85) with 95% confidence (target ≥80%)"
  - **NEGOTIATE**: "Moderate site: score 72.1/100 (target ≥70) with 75% confidence (target ≥65%). Negotiate favorable terms."
  - **PASS**: "Below threshold: score 51.9/100 (need ≥70) or confidence 65% (need ≥65%). Higher-scoring locations available."

- Includes confidence basis explanation:
  - "Based on data coverage: demographics 100%, competition 100%, transit 80%"

## Frontend Changes

### 3. ProvenanceTooltip Component ([frontend/components/ProvenanceTooltip.tsx](frontend/components/ProvenanceTooltip.tsx))

New component that displays on hover/click:
- **Score Breakdown Table**: Shows all metrics with:
  - Emoji indicators (👥 Population, 💰 Income, 🚇 Transit, 🏪 Competition, 🚗 Traffic)
  - Weighted score contribution
  - Raw values (e.g., "27000 people within 800m")
  - Data source name
  - Data coverage quality (High/Medium/Low)

- **Total Score**: Highlighted final score
- **Decision Reasoning**: Explains why PASS/NEGOTIATE/MAKE_OFFER
- **Data Sources Footer**: Emphasizes public data provenance

### 4. AddressListItem Updates ([frontend/components/AddressListItem.tsx](frontend/components/AddressListItem.tsx))

Enhanced the card component:
- **Info Icon** next to score: Triggers ProvenanceTooltip
- **Expandable Section**: "View score breakdown"
  - Visual progress bars showing relative contribution of each metric
  - Score components with weighted values
  - List of unique data sources

- **Decision Reasoning**: Inline display when provenance tooltip not shown

### 5. Type Definitions ([frontend/app/recommend/page.tsx](frontend/app/recommend/page.tsx))

Updated `RecommendedAddress` interface to include:
- `decision_reasoning?: string`
- `provenance?: ScoreProvenance`

## User Experience

### Before
- Score: 51.9 (no explanation)
- Decision: "Pass" (no reasoning)
- Confidence: 95% (no basis)

### After
Users can now see:
1. **At a glance**: Info icon next to score
2. **On hover/click**: Full breakdown showing:
   - Population: 14.0 pts (50/100 × 28% weight) - Statistics Finland
   - Transit: 16.0 pts (80/100 × 20% weight) - Digitransit Finland
   - Competition: 12.0 pts (80/100 × 15% weight) - OpenStreetMap
   - Income: 15.4 pts (70/100 × 22% weight) - PAAVO (placeholder)
   - Traffic: 6.0 pts (60/100 × 10% weight) - Traffic model (placeholder)
3. **Decision reasoning**: "Below threshold: score 51.9/100 (need ≥70). Higher-scoring locations available."
4. **Expandable details**: Visual representation of score components

## Data Sources Tracked

Currently tracking 5 public data sources:
1. **Statistics Finland Population Grid 2023** - Demographics
2. **Digitransit Finland API** - Transit access
3. **OpenStreetMap Overpass API** - Competition analysis
4. **PAAVO Postal Demographics** - Income data (placeholder)
5. **Traffic model** - Traffic volume (placeholder)

## Future Enhancements

- Add data freshness timestamps per source
- Include data coverage maps
- Add source reliability scoring
- Link to original data sources (URLs)
- Show historical score changes when data refreshes
- Add "Report Data Issue" button for user feedback

## Testing

To test the provenance display:
1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Search for addresses in Helsinki
4. Click the ℹ️ icon next to any score
5. Expand "View score breakdown"

## Notes

- All provenance data is automatically generated during scoring
- No additional API calls required
- Works seamlessly with existing SSE streaming architecture
- Fully backward compatible (old clients ignore new fields)
