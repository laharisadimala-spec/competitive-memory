#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/frontend"
npm install --legacy-peer-deps
npm run dev
