# Builds a Windows distributable into dist\AirWriting\
# Run from project root with .venv activated (or use the launcher logic below).
$ErrorActionPreference = 'Stop'

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ProjectDir

if (Test-Path '.venv\Scripts\python.exe') {
    $py = '.venv\Scripts\python.exe'
} else {
    Write-Host 'No .venv found. Run: python -m venv .venv ; .venv\Scripts\activate ; pip install -r requirements.txt'
    exit 1
}

if (Test-Path 'build')   { Remove-Item -Recurse -Force 'build' }
if (Test-Path 'dist')    { Remove-Item -Recurse -Force 'dist' }
if (Test-Path 'AirWriting.spec') { Remove-Item -Force 'AirWriting.spec' }

Write-Host 'Building AirWriting.exe with PyInstaller...'
& $py -m PyInstaller `
    --noconfirm `
    --name AirWriting `
    --collect-all mediapipe `
    --collect-all easyocr `
    --collect-data scipy `
    --hidden-import skimage `
    --paths src `
    src\main.py

if ($LASTEXITCODE -ne 0) { Write-Error 'PyInstaller build failed.'; exit 1 }

# Pre-bundle the hand landmarker model next to the .exe so users don't need
# internet on first run. Download if missing.
$modelsDir = 'dist\AirWriting\models'
New-Item -ItemType Directory -Force $modelsDir | Out-Null
$modelDst = Join-Path $modelsDir 'hand_landmarker.task'
if (-not (Test-Path $modelDst)) {
    Write-Host 'Downloading hand_landmarker.task into bundle...'
    Invoke-WebRequest `
        -Uri 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task' `
        -OutFile $modelDst
}

# Drop a launcher .bat alongside the .exe for users who prefer that.
Copy-Item -Path 'README.md', 'LICENSE' -Destination 'dist\AirWriting' -Force

Write-Host ''
Write-Host 'Build complete. Output: dist\AirWriting\AirWriting.exe'
$size = (Get-ChildItem -Recurse 'dist\AirWriting' | Measure-Object -Property Length -Sum).Sum
'Total bundle: {0:N1} MB' -f ($size / 1MB)
