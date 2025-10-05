# Requires -Version 5.1
Param(
  [string]$PythonExe = "python"  # override: .\install_all.ps1 -PythonExe python3
)

$ErrorActionPreference = "Stop"

# Exécuter depuis la racine
Set-Location -Path $PSScriptRoot

$BACKEND_DIR  = "Backend"
$FRONTEND_DIR = "frontend"
$VENV_DIR     = ".venv"

# Détection Python
try {
  & $PythonExe --version | Out-Null
} catch {
  if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonExe = "python3"
  } else {
    Write-Error "Python 3 isn't found ou not detected in PATH."
  }
}
Write-Host ("🔧 Python utilisé: " + (& $PythonExe --version))

# Backend venv
Write-Host "📦 Backend: venv creation -> $VENV_DIR"
& $PythonExe -m venv $VENV_DIR

# Activer venv
$venvActivate = ".\.venv\Scripts\Activate.ps1"
. $venvActivate

# Pip install
$req = Join-Path $BACKEND_DIR "requirements.txt"
if (-not (Test-Path $req)) {
  Write-Error "$req not found."
}
Write-Host "📦 Backend: pip install -r $req"
pip install --upgrade pip
pip install -r $req

# Frontend
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
  Write-Error "npm isn't installed. Install Node.js."
}
Write-Host "📦 Frontend: npm install"
Push-Location $FRONTEND_DIR
npm install
Pop-Location

Write-Host "✅ Installation completed."
Write-Host "➡️ To start: .\run.ps1"
