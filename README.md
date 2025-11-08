# Spotlight - AI-Powered Restaurant Site Selection

> Predict restaurant revenue for any location with multi-agent AI analysis

## 🎯 What is Spotlight?

Spotlight is an AI-powered platform that helps restaurant operators make data-driven site selection decisions. By analyzing demographics, competition, transit access, and foot traffic patterns, we predict monthly revenue potential for any location in the world, starting with Finland for the MVP.

**Our Moat:** Proprietary data flywheel. Each restaurant we help becomes a data sensor, capturing actual revenue and performance that makes all future predictions exponentially more accurate. With 100+ restaurants, we'll have prediction accuracy competitors cannot match with public data alone.

## 🚀 The Business Model

### Phase 1: Prediction Platform (Current)
- **Value Prop:** Predict where to open based on Finnish public data + multi-agent AI
- **Revenue:** €500-2000 per location analysis
- **Accuracy:** 85-90% with public data

### Phase 2: Data Flywheel (6-12 months)
- **Value Prop:** Predictions calibrated against real restaurant performance data
- **Revenue:** €1000/month subscription + benchmarking
- **Accuracy:** 92-95% with 10-50 customer performance data

### Phase 3: Network Effects (2+ years)
- **Value Prop:** The definitive restaurant performance dataset in Finland
- **Revenue:** €2000/month + performance optimization insights
- **Accuracy:** 95%+ with 100+ restaurant network data

### Phase 4: The Restaurant OS (Future)
- **Value Prop:** End-to-end restaurant intelligence platform
- **Revenue:** 3-5% of revenue share
- **Features:** Site selection, expansion timing, menu pricing, staffing, marketing optimization

## 🏗️ Technical Stack

**Backend:**
- FastAPI (Python) - Async API server
- Multi-agent AI system (7 specialized agents)
- Finnish public data integration (5 sources)
- SSE streaming for real-time progress

**Frontend:**
- Next.js 14 + React + TypeScript
- Google Maps integration
- Split-screen map view with interactive cards
- Real-time agent progress tracking

**Data Sources (All FREE!):**
- Digitransit - Finnish address geocoding
- Statistics Finland PAAVO - Postal code demographics
- Statistics Finland Population Grid - 1km grid population data
- OpenStreetMap Overpass - POIs, competitors, transit stops
- HSY - Helsinki metro area 250m grid population

## 🤖 The Agent System

Spotlight uses 7 specialized AI agents powered by GPT-4:

1. **GEO Agent** - Validates addresses and geocoding accuracy
2. **DEMO Agent** - Analyzes demographics vs. target customer profiles
3. **COMP Agent** - Evaluates competitive landscape and market gaps
4. **TRANSIT Agent** - Assesses public transit and walkability
5. **RISK Agent** - Calculates confidence scores and identifies risks
6. **REVENUE Agent** - Predicts monthly revenue (the core value prop)
7. **ORCHESTRATOR** - Coordinates all agents and synthesizes recommendations

**Why Agents?**
- Transparent reasoning: Every score includes "why"
- Specialization: Each agent focuses on one domain
- Composable: Easy to add new agents (e.g., Seasonal, Weather)
- Trust layer: Shows data quality and confidence for each metric

## 📊 How It Works

```
1. User enters: "casual_dining in Helsinki"

2. Data Collection (2s):
   - Geocode city → Find top neighborhoods
   - Fetch demographics, competitors, transit data

3. Multi-Agent Analysis (5s):
   GEO → Validates top 50 areas
   DEMO → Scores population fit (35% weight)
   COMP → Scores competition (25% weight)
   TRANSIT → Scores accessibility (20% weight)
   RISK → Calculates confidence
   REVENUE → Predicts €120k-150k/month

4. Results:
   - Top 10 ranked addresses
   - Split-screen: Cards + Interactive map
   - Click "Email Broker" → Pre-filled Gmail draft
   - Click "Plan Tour" → Multi-stop Google Maps route
```

## 🎨 Current Features

✅ **Recommendation Engine** - Top 10 addresses for any concept in any Finnish city
✅ **Split-Screen Map View** - Bidirectional sync between cards and pins
✅ **Real-time Progress** - SSE streaming shows agent execution stages
✅ **Email Broker Action** - One-click Gmail drafts with analysis
✅ **Multi-Stop Tours** - Generate walking routes for top 5 locations
✅ **Provenance Tracking** - Complete transparency of score calculations
✅ **Street View Integration** - Direct links to Google Street View

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Maps API key (get from https://console.cloud.google.com/)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your OpenAI API key if using agents (optional - agents currently disabled)

# Run backend
python3 -m uvicorn main:app --reload --port 8000
```

Backend runs on http://localhost:8000

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_key_here" >> .env.local

# Run frontend
npm run dev
```

Frontend runs on http://localhost:3000

### 3. Test It Out

1. Go to http://localhost:3000
2. Enter city: "Helsinki"
3. Select concept: "casual_dining"
4. Wait ~7 seconds for analysis
5. See top 10 locations with interactive map
6. Click any address to see details
7. Click "Email Broker" to generate outreach email
8. Click "Plan Tour (Top 5)" to get walking route

## 📁 Project Structure

```
/spotlight
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── agents/
│   │   └── agno/                  # Multi-agent system (GPT-4)
│   │       ├── orchestrator.py    # Coordinates all agents
│   │       ├── geo_agent.py       # Location validation
│   │       ├── demo_agent.py      # Demographics analysis
│   │       ├── comp_agent.py      # Competition analysis
│   │       ├── transit_agent.py   # Transit & accessibility
│   │       ├── risk_agent.py      # Confidence & risk assessment
│   │       └── revenue_agent.py   # Revenue prediction (CORE)
│   ├── services/                  # Finnish data source integrations
│   │   ├── digitransit.py         # Geocoding API
│   │   ├── statfin.py             # Demographics (PAAVO)
│   │   ├── population_grid.py     # 1km grid population
│   │   ├── hsy.py                 # Helsinki 250m grid
│   │   └── osm.py                 # OpenStreetMap (competitors, transit)
│   ├── routes/
│   │   └── recommend.py           # Recommendation endpoints + SSE
│   ├── models/
│   │   └── schemas.py             # Pydantic models (with provenance)
│   └── config/
│       └── concepts.yaml          # Restaurant concept parameters
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx               # Home page (search form)
│   │   └── recommend/
│   │       └── page.tsx           # Results page (split-screen map)
│   ├── components/
│   │   ├── MapView.tsx            # Google Maps integration
│   │   ├── AddressListItem.tsx    # Condensed result cards
│   │   ├── DecisionCard.tsx       # Detailed result cards (legacy)
│   │   └── ProvenanceTooltip.tsx  # Score breakdown transparency
│   └── lib/
│       ├── api.ts                 # Backend API client
│       └── types.ts               # TypeScript types
│
└── docs/                          # Documentation
    ├── AGENTS.md                  # Agent system architecture
    ├── IMPLEMENTATION_SUMMARY.md  # Technical implementation details
    └── TRUST_LAYER.md             # Transparency & provenance design
```

## 🔌 API Endpoints

### Recommendation Flow
- `POST /api/recommend` - Start recommendation job (returns job_id)
- `GET /api/stream/{job_id}` - SSE stream for real-time progress
- `GET /api/job/{job_id}` - Poll job status (fallback)

### Execution Actions
- `POST /api/pursue` - Generate broker email draft

### Discovery (Legacy)
- `POST /api/discover` - City-wide discovery view
- `POST /api/area/{area_id}` - Area details

## 🎯 Competitive Analysis

| Competitor | Has Predictions? | Has Reality Data? | Moat? |
|------------|-----------------|-------------------|-------|
| **Google Maps** | ❌ | ❌ | Search/reviews |
| **Yelp** | ❌ | ❌ | Reviews |
| **Real Estate Analytics** | ❌ | ❌ | Property data |
| **POS Systems (Toast, Square)** | ❌ | ✅ (revenue only) | Transaction processing |
| **Spotlight** | ✅ | ✅ (prediction → reality loop) | **Data flywheel** |

**Our Moat:** We're the only platform building the prediction → reality dataset. Every restaurant we help makes our predictions better for everyone.

## 🔮 Roadmap

### Q1 2025 (MVP)
- ✅ Multi-agent recommendation engine
- ✅ Split-screen map view
- ✅ Email broker action
- ✅ Provenance tracking
- ⏳ Performance tracking dashboard (for data collection)

### Q2 2025 (First Customers)
- ⏳ Onboard 5-10 pilot restaurants
- ⏳ Start collecting actual revenue data
- ⏳ Build benchmarking dashboard
- ⏳ Recalibrate models with real data

### Q3 2025 (Network Effects)
- ⏳ Expand to 50 restaurants
- ⏳ Launch subscription tier with benchmarks
- ⏳ Add seasonal performance predictions
- ⏳ Build customer success playbooks

### Q4 2025 (Scale)
- ⏳ 100+ restaurant network
- ⏳ Launch optimization features (menu pricing, staffing)
- ⏳ Expand to other Nordic countries
- ⏳ Build marketplace for commercial properties

## 🧪 Test Addresses (Helsinki)

Use these for testing:

**High Score Areas:**
- Mannerheimintie 20, Helsinki (Kamppi - high foot traffic)
- Aleksanterinkatu 15, Helsinki (City center - premium)

**Medium Score Areas:**
- Hämeentie 15, Helsinki (Kallio - emerging)
- Bulevardi 10, Helsinki (Design District)

**Lower Score Areas:**
- Ratapihantie 11, Helsinki (Pasila - office district)
- Itäkatu 1, Helsinki (Residential, low density)

## 🐛 Troubleshooting

**Backend won't start:**
- Check Python 3.9+ installed: `python --version`
- Activate virtual environment first
- Port 8000 available: `lsof -i :8000`

**Frontend won't start:**
- Check Node 18+ installed: `node --version`
- Delete `node_modules` and run `npm install` again
- Check `.env.local` has both API_URL and GOOGLE_MAPS_API_KEY

**Map not loading:**
- Check Google Maps API key in `.env.local`
- Verify key has "Maps JavaScript API" enabled in Google Cloud Console
- Check browser console for errors
- Restart Next.js dev server after adding `.env.local`

**Recommendations taking too long:**
- Check backend terminal for errors
- Verify all Finnish data sources are accessible
- SSE should show progress in browser console

**Email button not working:**
- Check backend `/api/pursue` endpoint is working
- Verify browser allows popup windows for Gmail
- Check browser console for CORS errors

## 📄 License

Proprietary - Spotlight 2025

---

**Built with ❤️ for restaurant operators who deserve better data**
