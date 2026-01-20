# run-dev.ps1
# Odpalaj z root folderu projektu.
# Wymaga Windows Terminal (wt).

$ErrorActionPreference = "Stop"

# PORTY (twoje)
$DAC_PORT = 8000
$AAC_PORT = 8001
$FC_PORT  = 8002
$UI_PORT  = 5173
$DV_PORT  = 5174

# Sciezki (wzgledem root)
$aacDir = Join-Path $PSScriptRoot "backend\alerts-authentication-and-communication"
$dacDir = Join-Path $PSScriptRoot "backend\data-access-and-control"
$fcDir  = Join-Path $PSScriptRoot "backend\forecast-and-optimization"
$uiDir  = Join-Path $PSScriptRoot "frontend\ui-ux"
$dvDir  = Join-Path $PSScriptRoot "frontend\data-visualization"

function Assert-Dir($p) {
  if (-not (Test-Path $p)) { throw "Folder nie istnieje: $p" }
}

Assert-Dir $aacDir
Assert-Dir $dacDir
Assert-Dir $fcDir
Assert-Dir $uiDir
Assert-Dir $dvDir

# Komendy
# AAC: jak prosiles: py main.py (port najpewniej masz w kodzie/env na 8001)
$aacCmd = "cd `"$aacDir`"; py main.py"

# DAC / FORECAST: uvicorn z jawnie ustawionym portem
$dacCmd = "cd `"$dacDir`"; uvicorn app.main:app --reload --host 127.0.0.1 --port $DAC_PORT"
$fcCmd  = "cd `"$fcDir`";  uvicorn app.main:app --reload --host 127.0.0.1 --port $FC_PORT"

# UI/UX i DV: npm run dev na konkretnych portach
# UWAGA: to dziala, jesli Vite respektuje --port (standardowo respektuje).
$uiCmd  = "cd `"$uiDir`"; npm run dev -- --host 127.0.0.1 --port $UI_PORT"
$dvCmd  = "cd `"$dvDir`"; npm run dev -- --host 127.0.0.1 --port $DV_PORT"

# Start: 5 tabow w jednym oknie
wt `
  new-tab -p "Windows PowerShell" -d "$aacDir" --title "AAC :$AAC_PORT" powershell -NoExit -Command $aacCmd `
  ; new-tab -p "Windows PowerShell" -d "$dacDir" --title "DAC :$DAC_PORT" powershell -NoExit -Command $dacCmd `
  ; new-tab -p "Windows PowerShell" -d "$fcDir"  --title "FORECAST :$FC_PORT" powershell -NoExit -Command $fcCmd `
  ; new-tab -p "Windows PowerShell" -d "$uiDir"  --title "UI/UX :$UI_PORT" powershell -NoExit -Command $uiCmd `
  ; new-tab -p "Windows PowerShell" -d "$dvDir"  --title "DV :$DV_PORT" powershell -NoExit -Command $dvCmd
