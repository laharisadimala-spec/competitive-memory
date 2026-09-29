@echo off
cd /d %~dp0
if not exist .env copy .env.example .env >nul
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
) else (
  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
)
