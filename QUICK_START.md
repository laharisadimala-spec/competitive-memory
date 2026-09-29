# Quick Start Guide

**Get Competitive Memory running in 5 minutes.**

## Prerequisites

- Python 3.10+ 
- Node.js 18+
- npm

## Installation

### 1. Backend Setup (2 minutes)

```bash
# Install Python dependencies
pip install --break-system-packages -r requirements.txt

# Start backend server
python -m uvicorn backend.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
✓ Competitive Memory initialized
✓ Loaded 21 events across 4 competitors
✓ Memory service: Demo Mode
```

**API docs:** Open http://localhost:8000/docs

### 2. Frontend Setup (2 minutes)

In a new terminal:

```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Start development server
npm run dev
```

**Expected output:**
```
  VITE v5.0.0  ready in 123 ms

  ➜  Local:   http://localhost:5173/
```

### 3. Access the App (1 minute)

Open your browser to: **http://localhost:5173**

You should see:
- Competitive Memory header with 🧠 emoji
- Timeline of ApexAI events
- Navigation tabs: Timeline, Strategy, Investigate, War Room, Memory

## First Steps

1. **View Timeline**: See 6 months of competitor events
2. **Check Strategy**: Detect ApexAI's shift to enterprise-first
3. **Investigate**: Ask "Is ApexAI moving to enterprise?" → See confidence score + evidence
4. **War Room**: Compare all 4 competitors
5. **Memory Explorer**: See actual Hindsight-backed memories

## Demo Dataset

The app ships with 4 companies over 6 months:

- **ApexAI**: SMB → Enterprise transformation (9 events)
- **CloudForge**: Steady infrastructure focus (3 events)
- **DataPulse**: Pricing war + upmarket move (4 events)
- **OrbitWorks**: Crisis → government pivot (4 events)

Use ApexAI for the best demo - clearest strategy shift story.

## Environment Variables (Optional)

Create `.env` file for Hindsight integration:

```env
HINDSIGHT_API_KEY=your_key_here
HINDSIGHT_BANK_ID=your_bank_id
# HINDSIGHT_BANK_ID is also accepted for backwards compatibility
DEMO_MODE=false
```

Without credentials, app uses Demo Memory Mode (clearly labeled, fully functional).

## Troubleshooting

### Backend won't start
```bash
# Make sure you're in the project root
python -m uvicorn backend.main:app --reload

# Check Python version
python --version  # Should be 3.10+
```

### Frontend won't load
```bash
# Navigate to frontend directory
cd frontend

# Clear npm cache
npm cache clean --force

# Reinstall
npm install --legacy-peer-deps

# Start
npm run dev
```

### API connection errors
- Ensure backend is running on http://localhost:8000
- Ensure frontend is running on http://localhost:5173
- Check browser console for errors (F12)
- Try hard refresh in browser (Cmd+Shift+R / Ctrl+Shift+R)

### Port conflicts
```bash
# If port 8000 is taken, run backend on different port
python -m uvicorn backend.main:app --port 9000

# If port 5173 is taken, run frontend on different port
cd frontend && npm run dev -- --port 5174

# Update frontend API URL in `src/App.tsx` if needed
```

## Running Tests

```bash
# Run backend tests
pytest tests/test_backend.py -v

# Expected: 16/16 passing
```

## Project Structure

```
competitive-memory/
├── backend/          # FastAPI backend
│   └── main.py      # Start here
├── frontend/        # React frontend
│   └── src/App.tsx  # Start here
├── data/            # Synthetic dataset
├── tests/           # Test suite
├── README.md        # Full documentation
├── DEMO_GUIDE.md    # Demo instructions
└── QUICK_START.md   # This file
```

## Key Features to Demo

1. **Timeline** - All competitor events in chronological order
2. **Strategy Detection** - Automatic strategy profile + shifts
3. **First Signal** - Find when strategy change began
4. **Investigation** - Test hypotheses with evidence
5. **Prove/Disprove** - Show supporting and contradicting evidence
6. **We've Seen This Before** - Historical pattern matching via Hindsight memory
7. **War Room** - Multi-competitor comparison
8. **Memory Explorer** - Inspect actual Hindsight-backed memories

## Next Steps

- Read `README.md` for full documentation
- Check `DEMO_GUIDE.md` for demo flow
- Explore `backend/main.py` for API endpoints
- Check `frontend/src/App.tsx` for UI code

## Support

All code is documented. Check:
- `backend/services/*.py` - Service implementations
- `frontend/src/components/*.tsx` - React components
- `backend/models/competitor.py` - Data models

---

**That's it!** You now have a fully functional competitive intelligence system with Hindsight memory.

Time to explore patterns only a memory-backed system can see.
