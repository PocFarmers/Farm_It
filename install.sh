#!/usr/bin/env bash
set -euo pipefail

# Exécuter depuis la racine même si on lance le script ailleurs
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- Config ---
PYTHON_BIN="${PYTHON_BIN:-python3}"     # override: PYTHON_BIN=python ./install_all.sh
BACKEND_DIR="Backend"
FRONTEND_DIR="frontend"
VENV_DIR=".venv"

# Détection python si python3 absent
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  if command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    echo "❌ Python 3 not found. Install Python 3."
    exit 1
  fi
fi

echo "🔧 Python utilisé: $(${PYTHON_BIN} --version)"

# --- Backend ---
echo "📦 Backend: création venv -> ${VENV_DIR}"
"${PYTHON_BIN}" -m venv "${VENV_DIR}"

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip

REQ_FILE="${BACKEND_DIR}/requirements.txt"
if [[ ! -f "${REQ_FILE}" ]]; then
  echo "❌ ${REQ_FILE} not found."
  exit 1
fi

echo "📦 Backend: pip install -r ${REQ_FILE}"
pip install -r "${REQ_FILE}"

# --- Frontend ---
if ! command -v npm >/dev/null 2>&1; then
  echo "❌ npm found. Install Node.js (https://nodejs.org)."
  exit 1
fi

echo "📦 Frontend: npm install"
pushd "${FRONTEND_DIR}" >/dev/null
npm install
popd >/dev/null

echo "✅ Installation completed."
echo "➡️ Pour démarrer: ./run.sh"
