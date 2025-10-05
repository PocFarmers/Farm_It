# Farm It — Manual Run Guide (Frontend + Backend)

## About Farm It

**Farm It** is an educational simulation game that invites players to explore **sustainable farming** in a changing climate. Across **tropical**, **temperate**, **arid**, and **cold** islands, you’ll manage crops and resources while balancing productivity with environmental responsibility.

---

## Real Climate Data, Real Decisions

To ensure realism, Farm It integrates **NASA** satellite–derived datasets via the **POWER API** (Prediction Of Worldwide Energy Resources). Three key variables drive the in-game climate model:

- **T2M** — *Air temperature at 2 m*  
  Influences crop growth rates and **evapotranspiration** (water loss from soil and plants).

- **RH2M** — *Relative humidity at 2 m*  
  Affects **irrigation needs** and plant **water stress**.

- **PRECTOTCORR** — *Total corrected precipitation*  
  Determines **rainfall input** and **soil moisture** dynamics.

These datasets combine products such as **MERRA-2** and **IMERG**, with spatial resolutions typically ~**10–60 km**, providing authentic environmental variability.

---

## What This Means for Gameplay

Grounding decisions in real climate inputs enables players to:

- Plan **irrigation** based on humidity, temperature, and rainfall patterns.  
- Time **fertilization** and crop cycles to match local climate signals.  
- Optimize **land management** for long-term **resilience** and **resource efficiency**.  
- Preserve **biodiversity** while maintaining yields.

FarmIt demonstrates how **space data** can power **sustainable agriculture** and **climate action**—turning environmental signals into actionable, in-game strategy.

---

*Data source:* NASA POWER API (with inputs from MERRA-2 and IMERG).

# Installation

**This guide shows how to **manually** install and run the **FastAPI backend** and the **React (Vite) frontend**.**

---

## Prerequisites
You need **Node.js (LTS)** and **Python 3.10** installed.

### Install on macOS

**Option A — Homebrew (recommended)**
```bash
# Install Homebrew if needed:
#/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install node
brew install python@3.10
brew link python@3.10 --force --overwrite
# Verify
node -v && npm -v && python3 --version
```
---

**Option B - NVM (Node Version Manager)**
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# open a new terminal, then:
nvm install --lts
nvm use --lts
# Verify
node -v && npm -v
```

### Install on Ubuntu/Debian

```bash
# Node.js LTS
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Python 3.10
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.10 python3.10-venv python3.10-distutils

# (optional) Make python3 point to 3.10
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 2

# Verify
node -v && npm -v && python3 --version
```

## Install on Windows

**Option A — Winget (Windows 10/11)**
```
# Run in PowerShell (Admin)
winget install -e --id OpenJS.NodeJS.LTS
winget install -e --id Python.Python.3.10
# Verify (new PowerShell window)
node -v; npm -v; python --version
```

**Option B — Official installers**
* Node.js LTS: [Télécharger Node.js](https://nodejs.org/en/download)
* Python 3.10: [Télécharger Python 3.10](https://www.python.org/downloads/release/python-3100/)

# Required for ChatGPT inference

You need to create a .env file and copy the following line in it :
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Run the Backend (FastAPI)

### macOS / Linux

```
# from project root
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r Backend/requirements.txt

# Start (choose one)
uvicorn Backend.main:app --host 0.0.0.0 --port 8000 --reload
# or
python3 Backend/main.py
```

### Windows (PowerShell)

```bash
# from project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r Backend\requirements.txt

# Start (choose one)
uvicorn Backend.main:app --host 0.0.0.0 --port 8000 --reload
# or
python Backend\main.py
```

## Run the Frontend (React + Vite)

Open a new terminal and run:
```bash
cd frontend
npm install
npm run dev
```
Frontend: http://localhost:5173

## Quick Troubleshooting

* Blank page: check browser Console/Network; verify imports (default vs named) and that bundles aren’t 404.

* CORS: enable Vite proxy (above) or add CORS middleware in FastAPI.

* OpenAI key missing: set OPENAI_API_KEY in .env and restart the backend.

* SQLite schema mismatch: migrate (Alembic) or recreate local DB in dev.