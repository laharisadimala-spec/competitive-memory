@echo off
cd /d %~dp0\frontend
npm install --legacy-peer-deps
npm run dev
