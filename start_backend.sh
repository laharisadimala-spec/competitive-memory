#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
[ -f .env ] || cp .env.example .env
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
