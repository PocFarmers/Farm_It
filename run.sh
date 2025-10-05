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
  echo "❌ Venv introuvable (${VENV_DIR}). Lancez d'abord ./install_all.sh"
  exit 1
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

# Vérifs
command -v uvicorn >/dev/null 2>&1 || { echo "❌ uvicorn non trouvé. (pip install uvicorn)"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm non trouvé."; exit 1; }

# Démarre le backend
echo "🚀 Backend: http://${HOST}:${PORT}"
uvicorn "${BACKEND_DIR}.main:app" --host "${HOST}" --port "${PORT}" --reload &
BACK_PID=$!

cleanup() {
  echo ""
  echo "🛑 Arrêt en cours..."
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
