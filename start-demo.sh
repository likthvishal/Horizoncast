#!/usr/bin/env bash
# HorizonCast — local demo launcher (macOS / Linux)
set -e

cd "$(dirname "$0")"

echo ""
echo "============================================"
echo "  HorizonCast — Local Demo"
echo "============================================"
echo ""

if [ ! -d ".venv" ]; then
  echo "[1/4] Creating Python venv..."
  python3 -m venv .venv
else
  echo "[1/4] Python venv already exists."
fi

echo "[2/4] Installing backend deps..."
./.venv/bin/python -m pip install --upgrade pip --quiet
./.venv/bin/python -m pip install -r requirements-demo.txt --quiet

if [ ! -d "frontend/node_modules" ]; then
  echo "[3/4] Installing frontend deps..."
  (cd frontend && npm install --silent)
else
  echo "[3/4] Frontend node_modules already installed."
fi

echo "[4/4] Starting backend (:8000) and frontend (:3000)..."
echo ""
echo "  Frontend:  http://localhost:3000"
echo "  API docs:  http://localhost:8000/docs"
echo ""

trap 'kill 0' EXIT
./.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload &
(cd frontend && npm run dev) &
wait
