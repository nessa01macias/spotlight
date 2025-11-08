# Spotlight View Specifications

**Detailed specifications for each view in the application**

---

## View 1: Landing Page (`/`)

### Purpose
Single entry point for all user searches. Intelligently routes to discovery or analysis based on input type.

### Layout

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                      Spotlight                          │
│      Evidence-based site selection for Finland         │
│                                                         │
│   ┌──────────────────────────────────────────────┐    │
│   │                                                │    │
│   │  helsinki_________________________  [🔍]      │    │
│   │                                                │    │
│   └──────────────────────────────────────────────┘    │
│                                                         │
│   Try: [Helsinki] [00100] [Kamppi 5]                  │
│                                                         │
│   ────────────────────────────────────────────────     │
│                                                         │
│   © 2025 Spotlight. Powered by public Finnish          │
│   data sources.                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Elements

**Search Input**
- Component: `<UniversalSearch />`
- Placeholder: "Search city, postal code, or address..."
- Auto-focus on page load
- Clear input button (×)
- Keyboard: Enter to submit

**Example Suggestions**
- Clickable pills that populate search
- Examples: "Helsinki", "00100", "Kamppi 5"
- Updates based on recent searches (future)

**Footer**
- Copyright
- "Powered by public Finnish data sources"
- "How we score" link (future modal)

### User Actions

1. **Type query + Enter**
   - Calls `/api/search`
   - Routes based on `search_type`
   - Shows loading spinner during API call

2. **Click example suggestion**
   - Populates search input
   - Auto-submits

3. **Click "How we score"** (future)
   - Opens modal explaining methodology
   - Shows agent descriptions

### States

**Idle**
- Empty search input
- Example suggestions visible

**Loading**
- Spinner in search button
- Input disabled
- "Detecting search type..."

**Error**
- Red border on input
- Error message below: "Could not parse search. Try 'Helsinki' or 'Mannerheimintie 1'"

### Routing Logic

```
Input: "Helsinki"       → /discover?city=Helsinki
Input: "00100"          → /discover?city=00100
Input: "Address"        → /analyze?addresses=Address
Input: "Addr1\nAddr2"   → /analyze?addresses=Addr1;Addr2
```

### Future Enhancements

- Search history dropdown
- Voice input
- Autocomplete suggestions
- "Paste 3 addresses" shortcut button
- Quick stats: "Analyzed 1,847 locations"

---

## View 2: Discovery View (`/discover`)

### Purpose
City-wide or area-wide exploration. Shows heatmap of opportunities across a region.

### Layout

```
┌─────────────────────────────────────────────────────────┐
│ ← Back to Search          📍 helsinki                  │
├─────────────────────────────────────────────────────────┤
│ Select Restaurant Concept                               │
│ [Quick Service] [Fast Casual] [Coffee Shop]            │
│ [Casual Dining ✓] [Fine Dining]                        │
├─────────────────────────────────────────────────────────┤
│ Areas Analyzed: 8              Concept: Casual Dining   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                  [MAP WITH HEATMAP]                     │
│                                                         │
│  Red markers = High opportunity (score 70-100)         │
│  Yellow markers = Medium opportunity (score 40-69)     │
│  Blue markers = Low opportunity (score 0-39)           │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ Top Opportunities                                       │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ #1  Kamppi                             54.4     │   │
│ │     Lat: 60.1699, Lng: 24.9342                  │   │
│ │                                                  │   │
│ │     Predicted Revenue                           │   │
│ │     €935,000 - €1,265,000                       │   │
│ │                                                  │   │
│ │     Est. Rent                                    │   │
│ │     €42/sqft                                     │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ #2  Töölö                              50.1     │   │
│ │     ...                                          │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ... (shows top 10)                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Components

**Header**
- Back button: Returns to landing page
- City name badge: Shows current city/postal code

**Concept Selection**
- Toggle group of 5 concepts
- Selected concept highlighted (purple)
- On change: Re-fetches discovery data

**Map**
- Component: `<HeatMap />`
- Library: MapBox GL
- Layers:
  - Base map (streets)
  - Heatmap layer (gradient red → blue)
  - Marker layer (top 10 locations)
- Controls: Zoom, pan, reset view
- On marker click: (Future) Navigate to area detail

**Top Opportunities List**
- Scrollable list of cards
- Sorted by score (descending)
- Each card shows:
  - Rank badge (#1, #2, etc.)
  - Area name
  - Score (large, colored by range)
  - Coordinates
  - Revenue range
  - Rent estimate
  - Property count
- On card click: (Future) Navigate to area detail

### User Actions

1. **Change Concept**
   - Calls `/api/discover` with new concept
   - Shows loading overlay on map
   - Updates heatmap + list

2. **Click Map Marker** (Future)
   - Highlights corresponding card in list
   - Scrolls list to card
   - Opens detail modal

3. **Click Opportunity Card** (Future)
   - Navigates to area detail view
   - Shows available properties
   - Option to analyze specific address

4. **Back to Search**
   - Returns to landing page
   - Clears discovery state

### States

**Loading**
- Skeleton cards in list
- Loading overlay on map
- "Scoring areas for casual dining..."

**Loaded - Has Results**
- Map with heatmap visible
- Top 10 list populated
- Summary: "8 areas analyzed"

**Loaded - No Results**
- Empty state message
- "No data available for this city yet"
- Suggestion: "Try Helsinki, Espoo, or Vantaa"

**Error**
- Error banner: "Failed to load discovery data"
- Retry button

### Data Display

**Score Coloring**
- 85-100: Dark green (#047857)
- 70-84: Green (#10B981)
- 55-69: Yellow (#F59E0B)
- 40-54: Orange (#F97316)
- 0-39: Red (#EF4444)

**Revenue Formatting**
- Finnish locale: €935 000 (with thin space)
- Ranges: €935k - €1.27M

### Responsive Behavior

**Desktop (>1024px)**
- Map on left (60% width)
- List on right (40% width)
- Side-by-side layout

**Tablet (768-1024px)**
- Map on top (full width, 50% height)
- List below (full width, scrollable)

**Mobile (<768px)**
- Tabs: [Map] [List]
- Only one visible at a time
- List defaults to active

### Future Enhancements

- Filter by score (min 70)
- Filter by rent (max €50/sqft)
- Filter by properties available
- Sort options (score, rent, properties)
- Save favorite areas
- Export top 10 to PDF
- Share discovery link

---

## View 3: Analysis View (`/analyze`)

### Purpose
Deep analysis of specific address(es). Shows predictions with transparent reasoning from Agno agents.

### Layout - Single Address

```
┌─────────────────────────────────────────────────────────┐
│ ← Back to Search                                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Mannerheimintie 1, Helsinki                            │
│                                                         │
│ ┌───────────────────────────────────────────────┐     │
│ │  Score: 87/100                    ⭐ Highly    │     │
│ │                                   Recommended  │     │
│ └───────────────────────────────────────────────┘     │
│                                                         │
│ ┌───────────────────────────────────────────────┐     │
│ │  Predicted Revenue (Year 1)                    │     │
│ │  €145,000/month                                │     │
│ │                                                 │     │
│ │  Range: €95k - €185k                           │     │
│ │  Confidence: 89%                                │     │
│ │                                                 │     │
│ │  [─────────●─────────] 89%                     │     │
│ └───────────────────────────────────────────────┘     │
│                                                         │
│ ┌───────────────────────────────────────────────┐     │
│ │  Key Strengths                                  │     │
│ │  ✓ High population density (8,900/km²)         │     │
│ │  ✓ Median income €48k matches target market    │     │
│ │  ✓ Excellent transit access                     │     │
│ └───────────────────────────────────────────────┘     │
│                                                         │
│ ┌───────────────────────────────────────────────┐     │
│ │  Key Concerns                                   │     │
│ │  ⚠ 12 competitors in 1km radius                │     │
│ └───────────────────────────────────────────────┘     │
│                                                         │
│ [Show Full Reasoning ↓]                                │
│                                                         │
│ ┌───────────────────────────────────────────────┐     │
│ │  GEO Agent Analysis                             │     │
│ │  Address successfully geocoded with high        │     │
│ │  precision. Location validated in dense urban   │     │
│ │  core of Helsinki. Data quality score: 95/100.  │     │
│ │                                                 │     │
│ │  DEMO Agent Analysis                            │     │
│ │  Demographics score 85/100. Population density  │     │
│ │  8,900/km² is optimal for casual dining...      │     │
│ │                                                 │     │
│ │  ... (all 6 agent traces)                       │     │
│ └───────────────────────────────────────────────┘     │
│                                                         │
│ ┌───────────────────────────────────────────────┐     │
│ │  Detailed Features                              │     │
│ │  ├─ Population (1km): 28,000                    │     │
│ │  ├─ Density: 8,900/km²                          │     │
│ │  ├─ Median Income: €48,000                      │     │
│ │  ├─ Competitors: 12 in 1km                      │     │
│ │  ├─ Metro: 280m away                            │     │
│ │  └─ Tram: 120m away                             │     │
│ └───────────────────────────────────────────────┘     │
│                                                         │
│ [Export to PDF]  [Share Results]                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Layout - Multiple Addresses (Comparison)

```
┌─────────────────────────────────────────────────────────┐
│ ← Back to Search                                        │
├─────────────────────────────────────────────────────────┤
│ Comparison Results - Ranked by Opportunity              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌───────────────────────────────────────────────┐     │
│ │ #1 ✅ Mannerheimintie 1, Helsinki      87     │     │
│ │                                                 │     │
│ │ Recommendation: MAKE OFFER                      │     │
│ │ Revenue: €145k/mo (€95k - €185k)               │     │
│ │ Confidence: 89%                                 │     │
│ │                                                 │     │
│ │ Strengths:                                      │     │
│ │ • High population density                       │     │
│ │ • Excellent transit access                      │     │
│ │                                                 │     │
│ │ [Show Reasoning ↓]                             │     │
│ └───────────────────────────────────────────────┘     │
│                                                         │
│ ┌───────────────────────────────────────────────┐     │
│ │ #2 ⚠️ Hämeentie 5, Helsinki            72     │     │
│ │                                                 │     │
│ │ Recommendation: NEGOTIATE                       │     │
│ │ Revenue: €120k/mo (€80k - €160k)               │     │
│ │ Confidence: 72%                                 │     │
│ │                                                 │     │
│ │ Concerns:                                       │     │
│ │ • High crime risk in area                       │     │
│ │ • Lower income demographics                     │     │
│ │                                                 │     │
│ │ [Show Reasoning ↓]                             │     │
│ └───────────────────────────────────────────────┘     │
│                                                         │
│ ┌───────────────────────────────────────────────┐     │
│ │ #3 ❌ Bulevardi 12, Helsinki           55     │     │
│ │                                                 │     │
│ │ Recommendation: PASS                            │     │
│ │ Revenue: €95k/mo (€65k - €125k)                │     │
│ │ Confidence: 65%                                 │     │
│ │                                                 │     │
│ │ Concerns:                                       │     │
│ │ • Oversaturated market (20+ competitors)        │     │
│ │ • Limited transit access                        │     │
│ │                                                 │     │
│ │ [Show Reasoning ↓]                             │     │
│ └───────────────────────────────────────────────┘     │
│                                                         │
│ ⚠️ Cannibalization Warning:                            │
│ Sites #1 and #2 are only 1.2km apart. Opening both     │
│ may reduce individual performance by 10-15%.            │
│                                                         │
│ [Export Comparison]  [Share Results]                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Components

**Prediction Card** (single address)
- Address header
- Score badge (large, colored)
- Recommendation badge (emoji + text)
- Revenue prediction (prominent)
- Confidence bar (visual progress bar)
- Strengths list (checkmarks)
- Risks list (warning icons)
- Expandable reasoning section
- Detailed features accordion
- Action buttons (export, share)

**Comparison Card** (multiple addresses)
- Rank badge (#1, #2, #3)
- Recommendation emoji (✅⚠️❌)
- Address + score
- Recommendation text (MAKE OFFER / NEGOTIATE / PASS)
- Revenue + confidence
- Top 2 strengths OR concerns (depending on score)
- Expandable reasoning

**Cannibalization Warning**
- Alert banner (yellow/orange)
- Warning icon
- Distance between sites
- Estimated impact

### User Actions

1. **Expand "Show Reasoning"**
   - Accordion opens
   - Shows all 6 agent traces
   - Each agent has collapsible section
   - Syntax highlighting for technical details

2. **Export to PDF** (Future)
   - Generates PDF report
   - Includes map, predictions, reasoning
   - Downloads automatically

3. **Share Results** (Future)
   - Generates shareable link
   - Copied to clipboard
   - Can share with team

4. **Back to Search**
   - Returns to landing page
   - Option to save results before leaving

### States

**Loading**
- Progress indicator: "Analyzing address... (30s remaining)"
- Shows which agent is currently running:
  - "Collecting data..." (0-10s)
  - "GEO Agent analyzing..." (10-20s)
  - "DEMO Agent analyzing..." (20-30s)
  - etc.
- Cancel button (cancels API request)

**Loaded**
- Prediction card(s) visible
- Reasoning initially collapsed
- Smooth scroll to results

**Error - Geocoding Failed**
- Error card: "Could not find address"
- Suggestion: "Check spelling or try nearby street"
- Try again button

**Error - Agents Failed**
- Warning banner: "AI agents unavailable, using basic scoring"
- Prediction still shown (from old scorer)
- Lower confidence indicated
- Contact support link

### Data Display

**Recommendation Mapping**
```
Score 85-100, Confidence 80+ → 🌟 Highly Recommended → MAKE OFFER
Score 70-84, Confidence 65+  → ✅ Recommended → MAKE OFFER
Score 55-69, Confidence 50+  → ⚠️ Consider Alternatives → NEGOTIATE
Score <55 or Confidence <50  → ❌ Not Recommended → PASS
```

**Revenue Formatting**
- Main prediction: €145,000/month (bold, large)
- Range: €95k - €185k (smaller, muted)
- Confidence: 89% (with visual bar)

**Reasoning Traces**
- Markdown formatting
- Code highlighting for technical details
- Collapsible sections per agent
- Copy button for each trace

### Performance Indicators

**Analysis Time**
- Shows estimated time remaining
- Updates in real-time as agents complete
- "Analysis complete in 67 seconds"

**Agent Progress**
```
✓ GEO Agent (10s)
✓ DEMO Agent (12s)
✓ COMP Agent (9s)
✓ TRANSIT Agent (11s)
⏳ RISK Agent (in progress...)
⊟ REVENUE Agent (pending)
⊟ ORCHESTRATOR (pending)
```

### Future Enhancements

- Side-by-side comparison table
- Filter reasoning by agent
- Export individual agent reports
- Save to dashboard
- Schedule follow-up analysis
- Alert if area becomes available

---

## View 4: Outcome Tracking View (Future)

### Purpose
Submit actual revenue after opening. Builds competitive moat through outcome learning.

### Layout

```
┌─────────────────────────────────────────────────────────┐
│ Submit Opening Outcome                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Prediction for: Mannerheimintie 1, Helsinki            │
│ Date Predicted: Jan 15, 2025                            │
│                                                         │
│ ┌───────────────────────────────────────────────┐     │
│ │  Predicted Revenue                              │     │
│ │  €145,000/month                                │     │
│ │  Range: €95k - €185k                           │     │
│ │  Confidence: 89%                                │     │
│ └───────────────────────────────────────────────┘     │
│                                                         │
│ ┌───────────────────────────────────────────────┐     │
│ │  Actual Performance                             │     │
│ │                                                 │     │
│ │  Opening Date: [2025-03-15]                     │     │
│ │                                                 │     │
│ │  Actual Monthly Revenue:                        │     │
│ │  € [____________]                               │     │
│ │                                                 │     │
│ │  Notes (optional):                              │     │
│ │  [Exceeded expectations due to local events]    │     │
│ │  [_______________________________________]      │     │
│ │  [_______________________________________]      │     │
│ │                                                 │     │
│ └───────────────────────────────────────────────┘     │
│                                                         │
│ [Submit Outcome]                                        │
│                                                         │
│ Why submit outcomes?                                    │
│ Your feedback helps improve predictions for everyone.   │
│ We'll never share your revenue data.                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### After Submission

```
┌─────────────────────────────────────────────────────────┐
│ ✓ Outcome Recorded Successfully                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Mannerheimintie 1, Helsinki                            │
│                                                         │
│ ┌───────────────────────────────────────────────┐     │
│ │  Predicted: €145,000/month                     │     │
│ │  Actual: €152,000/month                        │     │
│ │                                                 │     │
│ │  Variance: +4.8%                                │     │
│ │  Status: ✓ Within predicted range              │     │
│ └───────────────────────────────────────────────┘     │
│                                                         │
│ Thank you for helping improve Spotlight!                │
│                                                         │
│ Your outcome has been added to our learning model.      │
│ Current accuracy: 92.3% of predictions within range.    │
│                                                         │
│ [View Your Predictions]  [Submit Another]               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Form Validation

**Opening Date:**
- Must be in past
- Must be after prediction date
- Format: YYYY-MM-DD

**Actual Revenue:**
- Required
- Must be positive number
- Format: €XXX,XXX

**Notes:**
- Optional
- Max 500 characters

### User Actions

1. **Submit Outcome**
   - Validates form
   - Calls `/api/outcomes`
   - Shows success screen

2. **View Your Predictions**
   - Shows dashboard of all predictions
   - Highlights those needing outcomes

3. **Submit Another**
   - Clears form
   - Ready for next submission

---

## Common UI Components

### ConfidenceBadge
```
High (80-100%)    → Green badge
Medium (60-79%)   → Yellow badge
Low (0-59%)       → Orange badge
```

### ScoreChip
```
85-100 → Dark green background
70-84  → Green background
55-69  → Yellow background
40-54  → Orange background
0-39   → Red background
```

### MethodModal
- Triggered by "How we score" link
- Explains 6 agents and their roles
- Shows sample reasoning trace
- Link to full documentation

### DataCoverageBar
- Visual indicator of data completeness
- Shows which data sources are available
- Example: "Geo ✓ | Demo ✓ | Competition ✓ | Transit ✓"

---

## Responsive Design

**Breakpoints:**
- Mobile: <768px
- Tablet: 768-1024px
- Desktop: >1024px

**Mobile Adjustments:**
- Stack all sections vertically
- Hide map by default (show in tab)
- Larger touch targets (48px min)
- Simplified navigation (hamburger menu)

**Tablet Adjustments:**
- Two-column grid where appropriate
- Map in upper panel, list below
- Collapsible sidebar for filters

**Desktop:**
- Full three-column layout
- Persistent sidebar
- Larger typography
- More whitespace
