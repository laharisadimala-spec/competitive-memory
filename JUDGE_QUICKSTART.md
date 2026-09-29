# Judge Quickstart

Get Competitive Memory running and tested in 2 minutes.

## Setup & Launch

1. **Install dependencies**
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install --legacy-peer-deps
   cd ..
   ```

2. **Start backend**
   ```bash
   start_backend.bat
   # Or: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

3. **Start frontend**
   ```bash
   start_frontend.bat
   # Or: cd frontend && npm run dev
   ```

4. **Open browser**
   - Application: [http://localhost:5173](http://localhost:5173)
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Recommended Judge Demo Flow

5. **Select ApexAI** from the top competitor selector.
6. **Open Timeline** to view chronological competitor intelligence signals.
7. **Open Strategy** to inspect the detected AI-first strategy and earliest signals.
8. **Click "We've Seen This Before"** on a timeline event to view historical pattern matching.
9. **Open Investigation** to test hypotheses with supporting/contradicting evidence trails.
10. **Open Memory Explorer** to view retained memories and test semantic recall queries.
