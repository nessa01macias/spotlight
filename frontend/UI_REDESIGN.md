# Spotlight UI Redesign - Complete Documentation

## Overview

This is a **Lovably-inspired clean redesign** of the Spotlight (ExpansionAI) frontend, focused on:
- **Trust & Explainability** - ConfidenceBadge, DataCoverageBar, MethodModal
- **EU Compliance** - No protected traits, transparent safety proxies
- **Conversion Optimization** - Max 2 CTAs per screen, sticky action bars
- **Clean Aesthetic** - Generous spacing, subtle shadows, blue-purple gradient palette

---

## Design System

### Color Palette

Your custom **blue-purple gradient** (F2F7FF → 9D71E8):

```typescript
gradient: {
  50: '#F2F7FF',   // Page backgrounds, very light
  100: '#C9DCFF',  // Card backgrounds, light fills
  200: '#B2C9FF',  // Secondary interactive
  300: '#BE99FF',  // Accents, hover states
  400: '#9D71E8',  // Primary CTA, dark accents
}
```

**WCAG Compliance:**
- Use dark text (`neutral-700`, `neutral-900`) on light gradient colors
- Use white text only on `gradient-400`
- All combinations meet WCAG AA standards

### Key Files

- **`lib/design-system.ts`** - Complete design tokens (colors, typography, spacing, utilities)
- **`tailwind.config.ts`** - Tailwind integration with gradient palette
- **`app/globals.css`** - Base styles (if needed)

---

## Components Built

### 📊 Trust Components (`components/trust/`)

#### 1. **ConfidenceBadge.tsx**
Color-coded confidence indicator with tooltip.

**Props:**
```typescript
interface ConfidenceBadgeProps {
  confidence: number;        // 0-1 scale
  dataCoverage?: number;     // 0-1 scale (default: 0.85)
  showModal?: boolean;       // Show info icon (default: true)
  onModalClick?: () => void;
}
```

**Color thresholds:**
- <0.6: Amber (low confidence)
- 0.6-0.75: Green (medium)
- 0.75-0.9: Emerald (high)
- ≥0.9: Dark emerald (very high)

**Example:**
```tsx
<ConfidenceBadge
  confidence={0.82}
  onModalClick={() => setShowMethodModal(true)}
/>
```

---

#### 2. **DataCoverageBar.tsx**
4-segment inline bar showing data completeness.

**Props:**
```typescript
interface DataCoverageBarProps {
  demographics?: number;  // 0-1 scale
  competition?: number;
  transit?: number;
  rent?: number;
}
```

**Segments:**
- Demographics (PAAVO, HSY)
- Competition (OSM)
- Transit access (Digitransit)
- Rent data (property listings)

**Example:**
```tsx
<DataCoverageBar
  demographics={0.95}
  competition={0.88}
  transit={0.92}
  rent={0.65}
/>
```

---

#### 3. **ScoreChip.tsx**
Large numeral pill showing opportunity score (0-100).

**Props:**
```typescript
interface ScoreChipProps {
  score: number;              // 0-100 scale
  maxScore?: number;          // Default: 100
  size?: 'sm' | 'md' | 'lg';
}
```

**Color thresholds:**
- ≥80: Green (high opportunity)
- 60-79: Amber (medium)
- <60: Red (low)

**Example:**
```tsx
<ScoreChip score={91} size="md" />
```

---

#### 4. **MethodModal.tsx**
"How we score" explainer modal with sources and timestamps.

**Props:**
```typescript
interface MethodModalProps {
  isOpen: boolean;
  onClose: () => void;
}
```

**Shows:**
- Scoring formula with weights (Population 35%, Income 25%, etc.)
- Revenue prediction formulas
- Data sources (PAAVO, HSY, Digitransit, OSM) with refresh times
- Confidence explanation

**Example:**
```tsx
const [showModal, setShowModal] = useState(false);

<MethodModal isOpen={showModal} onClose={() => setShowModal(false)} />
```

---

### 🎨 Core UI Components (`components/core/`)

#### 5. **MetricHero.tsx**
Large score + revenue display with confidence badge.

**Props:**
```typescript
interface MetricHeroProps {
  score: number;              // 0-100
  revenueMin: number;         // € amount
  revenueMax: number;         // € amount
  confidence: number;         // 0-1 scale
  title?: string;
  subtitle?: string;
  onMethodClick?: () => void;
}
```

**Features:**
- Big score display (6xl font)
- Revenue range with Finnish formatting (€1 600 000)
- ConfidenceBadge integration
- Warning banner if confidence <0.6

**Example:**
```tsx
<MetricHero
  score={91}
  revenueMin={1600000}
  revenueMax={1900000}
  confidence={0.82}
  title="Kamppi - University District"
  subtitle="Helsinki, Finland"
  onMethodClick={() => setShowMethodModal(true)}
/>
```

---

#### 6. **OpportunityCard.tsx**
Clean card for discovery view sidebar.

**Props:**
```typescript
interface OpportunityCardProps {
  name: string;
  score: number;
  revenueMin: number;
  revenueMax: number;
  confidence?: number;
  onView: () => void;
  onCompare?: () => void;
}
```

**Layout:**
- Area name + ScoreChip (right-aligned)
- Revenue range (muted text)
- Max 2 CTAs: [View →] [Compare]

**Example:**
```tsx
<OpportunityCard
  name="Kamppi - University District"
  score={91}
  revenueMin={1600000}
  revenueMax={1900000}
  confidence={0.82}
  onView={() => router.push('/area/kamppi')}
  onCompare={() => addToComparison('kamppi')}
/>
```

---

#### 7. **InsightList.tsx**
Bullets with inline numbers (not just checkmarks).

**Props:**
```typescript
export interface Insight {
  type: 'strength' | 'risk' | 'recommendation';
  text: string;
}

interface InsightListProps {
  insights: Insight[];
  title?: string;
}
```

**Example with inline math:**
```tsx
const insights: Insight[] = [
  {
    type: 'strength',
    text: '28,000 people within 1km; median income €48,000 (+6% vs target)',
  },
  {
    type: 'risk',
    text: '12 competitors nearby (0.43 per 1,000 people); manageable density',
  },
];

<InsightList title="Why this works" insights={insights} />
```

---

#### 8. **UniversalSearch.tsx** (Redesigned)
Large centered search with clickable example chips.

**New features:**
- Keyboard support (Enter to submit, focus ring)
- Clickable example chips that prefill and submit
- Gradient-themed focus states
- Size variants (`default` | `large`)

**Example:**
```tsx
<UniversalSearch size="large" />
```

---

#### 9. **HeatMap.tsx**
Mapbox with desaturated base, 2-color ramp.

**Features:**
- Clean, minimal style (no UI clutter)
- 2-color heatmap ramp (light green → emerald)
- Tooltips on hover (not legends)
- Graceful fallback if no Mapbox token

**Example:**
```tsx
<HeatMap
  center={[24.9384, 60.1695]}  // Helsinki
  zoom={11}
  data={opportunitiesGeoJSON}
  onAreaClick={(id) => router.push(`/area/${id}`)}
/>
```

---

### 🔧 UX Components (`components/ux/`)

#### 10. **StickyActionBar.tsx**
Bottom sticky bar with Compare/Download CTAs.

**Props:**
```typescript
interface StickyActionBarProps {
  onCompare?: () => void;
  onDownload?: () => void;
  compareLabel?: string;
  downloadLabel?: string;
  isLoading?: boolean;
}
```

**Default labels:**
- Compare: "Compare against top alternatives"
- Download: "Download investor-ready PDF"

**Example:**
```tsx
<StickyActionBar
  onCompare={() => router.push('/compare')}
  onDownload={() => generatePDF()}
/>
```

---

#### 11. **SkeletonCard.tsx**
Loading states (no spinners).

**Props:**
```typescript
interface SkeletonCardProps {
  variant?: 'card' | 'hero' | 'list';
  count?: number;
}
```

**Example:**
```tsx
{isLoading ? (
  <SkeletonCard variant="hero" />
) : (
  <MetricHero {...data} />
)}
```

---

#### 12. **ToggleGroup.tsx**
Filter toggles including "Safety proxy" with explainer.

**Props:**
```typescript
export interface Toggle {
  id: string;
  label: string;
  description?: string;
  defaultValue?: boolean;
  tooltip?: string;
}

interface ToggleGroupProps {
  title?: string;
  toggles: Toggle[];
  onChange?: (id: string, value: boolean) => void;
}
```

**Example:**
```tsx
const toggles: Toggle[] = [
  {
    id: 'safety-proxy',
    label: 'Safety proxy',
    description: 'Uses nightlife density + public stats',
    defaultValue: true,
    tooltip: 'Max 5% weight cap, correlation only',
  },
];

<ToggleGroup title="Filters" toggles={toggles} />
```

---

#### 13. **ComparisonTable.tsx**
Side-by-side with arrows + verdict row.

**Props:**
```typescript
export interface ComparisonSite {
  id: string;
  name: string;
  score: number;
  population: number;
  income: number;
  transitType: string;
  competitors: number;
  rent: number;
  revenueMin: number;
  revenueMax: number;
}

interface ComparisonTableProps {
  sites: ComparisonSite[];
  maxSites?: number;  // Default: 3 (strict limit)
}
```

**Features:**
- Side-by-side feature rows with comparison arrows (▲/▼/≈)
- Verdict row: "Kamppi wins by +7 score; +€0.2-0.3M revenue"
- Max 3 sites (strict limit)

**Example:**
```tsx
<ComparisonTable sites={[site1, site2, site3]} maxSites={3} />
```

---

#### 14. **Button.tsx**
Primary UI button with variants.

**Props:**
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'tertiary';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  disabled?: boolean;
}
```

**Example:**
```tsx
<Button variant="primary" size="md" onClick={handleClick}>
  Download Report
</Button>
```

---

## Pages

### Landing Page (`app/page.tsx`)

**Clean, minimal design:**
- Gradient background with grain texture
- Centered "Spotlight" title
- Subtitle: "Evidence-based site selection for Helsinki"
- Large UniversalSearch
- No clutter, no value props (moved to onboarding)

---

### Demo Page (`app/demo/page.tsx`)

**Complete component showcase** with realistic data:
- All trust components
- All core UI components
- All UX components
- Interactive toggles and modals

**Access:** Navigate to `/demo`

---

## Design Principles

### 1. Trust & Explainability
- **ConfidenceBadge** on every score
- **Inline math** in insights (e.g., "28k pop; €48k income +6%")
- **MethodModal** footer link + info icons
- **DataCoverageBar** shows source completeness

### 2. EU Compliance
- **No protected traits** in copy (no age %, no ethnicity)
- **Demand proxies** instead: "3 universities <500m" not "42% age 18-24"
- **Safety proxy toggle** visible, labeled "proxy - correlation only", max 5% weight

### 3. Conversion Optimization
- **Max 2 CTAs** per screen (View + Compare, Compare + Download)
- **StickyActionBar** on detail pages
- **Clickable example chips** on landing
- **Clear hierarchy** (big score, muted revenue, then actions)

### 4. Clean Aesthetic
- **Generous spacing** (8px, 16px, 24px, 32px increments)
- **Subtle shadows** (sm, md, lg - not dramatic)
- **Grain texture** <3% opacity (page backgrounds only, never maps)
- **Reduced radius** (0.75rem for buttons, 0.5rem for cards - enterprise vibes)
- **150ms transitions** with ease-out easing

---

## Formatting Utilities

From `lib/design-system.ts`:

```typescript
// Currency (Finnish locale, thin space)
formatCurrency(1600000) // "€1 600 000"

// Area
formatArea(223) // "223 m²"

// Rent
formatRent(42) // "42 €/m²/month"

// Confidence
formatConfidence(0.82) // { value: "82%", color: "#059669" }

// Score color
getScoreColor(91) // "#10B981"

// Confidence color
getConfidenceColor(0.82) // "#059669"
```

---

## Error/Empty States

### 1. No competitors found
```
"Low density area; confidence lowered; widen search band."
```

### 2. OSM rate limited
```
"Using cached POIs from 2 hours ago; refresh in ~22h."
```

### 3. Address outside Helsinki
```
"We currently support Helsinki Metro; try a city search."
```

### 4. No properties available
```
"No listed properties here right now.
We add listings weekly. Contact local brokers for off-market options.
[See nearby areas →]"
```

### 5. Low confidence (<0.6)
```
Warning banner: "Limited data coverage (Confidence 56%). Estimates widen to ±24%. Consider alternative areas."
```

### 6. Loading states
Use `<SkeletonCard />` instead of spinners.

---

## Running the Demo

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Set environment variables:**
   ```bash
   # .env.local
   NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token  # Optional for maps
   ```

3. **Start dev server:**
   ```bash
   npm run dev
   ```

4. **View pages:**
   - Landing: http://localhost:3000
   - Demo: http://localhost:3000/demo

---

## Next Steps

### Pages to Create

1. **Discovery View** (`app/discover/[city]/page.tsx`)
   - 60/40 split: HeatMap (60%) + Sidebar (40%)
   - Top 5-7 OpportunityCards
   - ToggleGroup for filters
   - Server-side preload top 5, lazy-load rest

2. **Area Detail** (`app/area/[id]/page.tsx`)
   - MetricHero at top
   - "Why this works" with InsightList
   - Available properties section (with empty state)
   - StickyActionBar: [Compare] [Download]

3. **Site Analysis** (`app/site/page.tsx`)
   - Same structure as Area Detail
   - Strengths/Risks/Recommendations sections
   - Finnish units (m², €/m²/month) with tooltip

4. **Comparison View** (`app/compare/page.tsx`)
   - ComparisonTable (max 3 sites)
   - Verdict row
   - StickyActionBar: [Download comparison PDF]

---

## Migration from Old Design

### Color replacements:

| Old Class | New Class | Notes |
|-----------|-----------|-------|
| `bg-primary-600` | `bg-gradient-400` | Primary CTA |
| `text-primary-600` | `text-gradient-400` | Primary text |
| `border-primary-200` | `border-gradient-200` | Borders |
| `bg-gray-50` | `bg-gradient-50` | Light backgrounds |
| `text-gray-600` | `text-neutral-600` | Muted text |
| `text-gray-900` | `text-neutral-900` | Dark text |

### Component replacements:

- Remove all `primary-*` color usage
- Replace spinners with `<SkeletonCard />`
- Replace multi-CTA layouts with max 2 buttons
- Add `<ConfidenceBadge />` to all score displays
- Add `<StickyActionBar />` to detail pages

---

## Accessibility

- **Keyboard navigation:** Focus ring on all interactive elements
- **WCAG AA contrast:** All color combinations meet standards
- **ARIA labels:** All buttons have descriptive labels
- **Screen reader support:** Semantic HTML throughout
- **Finnish locale:** €1 600 000 (thin space), m²/month

---

## Credits

**Design inspiration:** Lovably (lovable.dev)
**Color palette:** Custom blue-purple gradient (F2F7FF → 9D71E8)
**Framework:** Next.js 14 + Tailwind CSS
**Maps:** Mapbox GL JS
**Icons:** Heroicons

---

## Questions?

See the `/demo` page for a complete working example of all components.

For component props and usage, check the inline JSDoc comments in each component file.
