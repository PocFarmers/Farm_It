#!/usr/bin/env bash
set -euo pipefail

# Exécuter depuis la racine
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BACKEND_DIR="Backend"
FRONTEND_DIR="frontend"
VENV_DIR=".venv"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

# Active venv
if [[ ! -f "${VENV_DIR}/bin/activate" ]]; then
  echo "❌ Venv not found (${VENV_DIR}). Launch ./install_all.sh first"
  exit 1
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

# Vérifs
command -v uvicorn >/dev/null 2>&1 || { echo "❌ uvicorn not found. (pip install uvicorn)"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm not found."; exit 1; }

# Démarre le backend
echo "🚀 Backend: http://${HOST}:${PORT}"
uvicorn "${BACKEND_DIR}.main:app" --host "${HOST}" --port "${PORT}" --reload &
BACK_PID=$!

cleanup() {
  echo ""
  echo "🛑 Stop in progress..."
  kill "${BACK_PID}" 2>/dev/null || true
}
trap cleanup INT TERM

# Démarre le frontend (bloquant)
echo "🚀 Frontend: (Vite) http://localhost:5173"
pushd "${FRONTEND_DIR}" >/dev/null
npm run dev || true
popd >/dev/null

# Quand le dev server s'arrête, on coupe le backend
cleanup
