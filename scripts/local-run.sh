#!/usr/bin/env bash
# WHAT: One-command local dev bootstrap for Codespace or local machine.
# WHY: Reduces friction; ensures reproducible environment spin-up.
# HOW: Installs Python deps, starts FastAPI and frontend concurrently.

set -e

echo "[Backend] Installing Python deps..."
pip install -r backend/requirements.txt

echo "[Frontend] Installing Node deps..."
cd frontend
npm install
cd ..

echo "[Run] Starting backend (FastAPI) on port 8000..."
python -m uvicorn backend.main:app --port 8000 --reload &
BACKEND_PID=$!

echo "[Run] Starting frontend (Vite) on port 5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID | Frontend PID: $FRONTEND_PID"
echo "Press Ctrl+C to stop both."

wait