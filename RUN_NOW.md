# Competitive Memory — Run Now

## Windows

1. Open Command Prompt in this folder.
2. Install backend packages:

```bat
python -m pip install -r requirements.txt
```

3. Start the backend:

```bat
start_backend.bat
```

4. Open a second Command Prompt in the same folder and run:

```bat
start_frontend.bat
```

5. Open:

`http://localhost:5173`

Backend API docs:

`http://localhost:8000/docs`

## Hindsight Cloud

For real persistent Hindsight memory, create `.env` from `.env.example` and set:

```env
HINDSIGHT_API_KEY=your_key
HINDSIGHT_BANK_ID=your_bank_id
DEMO_MODE=false
```

Without credentials, the app runs in clearly labelled Demo Memory Mode and remains fully usable for the synthetic demo.

## Recommended demo

1. Timeline → ApexAI
2. Strategy → show strategy shift and first signal
3. Ask Memory → “What changed?”
4. Ask Memory → “Have we seen this before?”
5. Ask Memory → “What happened last time?”
6. Investigate → run the enterprise hypothesis
7. Prove it / Disprove it
8. Time Machine → travel back 90 days
9. Memory → recall pricing and enterprise history
10. War Room → compare all competitors
