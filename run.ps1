# Requires -Version 5.1
$ErrorActionPreference = "Stop"

# Exécuter depuis la racine
Set-Location -Path $PSScriptRoot

$BACKEND_DIR  = "Backend"
$FRONTEND_DIR = "frontend"
$VENV_DIR     = ".venv"

$HOST = $env:HOST
if ([string]::IsNullOrWhiteSpace($HOST)) { $HOST = "0.0.0.0" }
$PORT = $env:PORT
if ([string]::IsNullOrWhiteSpace($PORT)) { $PORT = "8000" }

# Activer venv
$venvActivate = ".\.venv\Scripts\Activate.ps1"
if (-not (Test-Path $venvActivate)) {
  Write-Error "Venv introuvable ($VENV_DIR). Lancez d'abord .\install_all.ps1"
}
. $venvActivate

# Vérifs
if (-not (Get-Command uvicorn -ErrorAction SilentlyContinue)) {
  Write-Error "uvicorn non trouvé (pip install uvicorn)"
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
  Write-Error "npm non trouvé (installez Node.js)"
}

# Démarrage backend
Write-Host "🚀 Backend: http://$HOST`:$PORT"
$backend = Start-Process -FilePath "uvicorn" -ArgumentList "$BACKEND_DIR.main:app","--host",$HOST,"--port",$PORT,"--reload" -PassThru

try {
  # Démarrage frontend (bloquant)
  Write-Host "🚀 Frontend: (Vite) http://localhost:5173"
  Push-Location $FRONTEND_DIR
  npm run dev
  Pop-Location
}
finally {
  Write-Host "🛑 Arrêt Backend"
  if ($backend -and -not $backend.HasExited) {
    Stop-Process -Id $backend.Id -Force
  }
}
