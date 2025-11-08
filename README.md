# ExpansionAI - Helsinki MVP

> Predict restaurant revenue for any location in 60 seconds

## Overview

This is the MVP for Lifeline Ventures demo - a restaurant site selection tool that predicts revenue using Finnish public data sources.

**Stack:**
- Backend: FastAPI (Python)
- Frontend: Next.js 14 + React + TypeScript + Mapbox
- Data: Statistics Finland, OSM, HSY, Digitransit

## Quick Start

### 1. Get Mapbox API Token

1. Go to https://account.mapbox.com/auth/signup/
2. Sign up (free, no credit card)
3. Copy your **Default public token** (starts with `pk.`)

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your Mapbox token (optional for backend)

# Run backend
python main.py
```

Backend will run on http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local
# Edit .env.local and add:
# NEXT_PUBLIC_MAPBOX_TOKEN=pk.your_actual_token_here

# Run frontend
npm run dev
```

Frontend will run on http://localhost:3000

## Testing the App

### Test Discovery Flow:
1. Go to http://localhost:3000
2. Type "Helsinki"
3. Select concept (e.g., "QSR")
4. See heatmap + top opportunities

### Test Address Analysis:
1. Paste address: "Mannerheimintie 20, Helsinki"
2. Select concept
3. See predicted revenue + analysis

### Test Multiple Addresses:
1. Paste 3 addresses (one per line or separated by semicolons)
2. See ranked comparison

## Demo Addresses (Helsinki)

Use these for testing:
- **Kamppi:** Mannerheimintie 20, Helsinki (high score)
- **Kallio:** Hämeentie 15, Helsinki (medium score)
- **Pasila:** Ratapihantie 11, Helsinki (lower score)

## Project Structure

```
/spotlight
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── agents/                 # Scoring & data collection
│   ├── services/               # Finnish data sources
│   ├── models/                 # Database & schemas
│   └── config/                 # Concept parameters
│
├── frontend/
│   ├── app/                    # Next.js pages
│   ├── components/             # React components
│   └── lib/                    # API client & types
```

## API Endpoints

- `POST /api/search` - Universal search (auto-detects city/address)
- `POST /api/discover` - Discovery view (heatmap)
- `POST /api/analyze` - Site analysis (predictions)
- `POST /api/outcomes` - Submit actual results (outcome learning)
- `GET /api/accuracy` - Model accuracy stats

## Data Sources (All FREE!)

✅ **Digitransit** - Geocoding (no key needed)
✅ **OpenStreetMap** - Competitors, transit, POIs (no key needed)
✅ **Statistics Finland** - Demographics (no key needed)
✅ **HSY** - Population grid (no key needed)
✅ **Mapbox** - Maps & heatmaps (free tier: 50k loads/month)

## Next Steps

### For Lifeline Demo:
1. ✅ Get Mapbox token
2. ✅ Run backend + frontend
3. ⏳ Build discovery view (heatmap)
4. ⏳ Build site analysis page
5. ⏳ Test with real Helsinki data
6. ⏳ Prepare demo script

### Future (Post-Demo):
- PDF report generation
- Database integration (PostgreSQL)
- Outcome tracking UI
- US market expansion (Phoenix, AZ)

## Troubleshooting

**Backend won't start:**
- Check Python version (3.9+)
- Verify virtual environment is activated
- Check port 8000 is available

**Frontend won't start:**
- Check Node version (18+)
- Run `npm install` again
- Check `.env.local` has Mapbox token

**Map not showing:**
- Verify Mapbox token in `.env.local`
- Check browser console for errors
- Token must start with `pk.`

**API calls failing:**
- Backend must be running on port 8000
- Check CORS settings in backend
- Verify API_URL in frontend `.env.local`

## License

Proprietary - ExpansionAI 2025
