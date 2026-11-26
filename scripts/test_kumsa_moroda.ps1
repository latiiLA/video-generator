# Test film: Kumsa Moroda (Afaan Oromo narration + English subtitles)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PYTHONPATH = (Get-Location).Path
$py = ".\.venv\Scripts\python.exe"
$sb = (Resolve-Path ".\storyboards\kumsa_moroda.json").Path

if (-not (Test-Path $py)) {
  throw "Create venv first: py -3 -m venv .venv; .\.venv\Scripts\python -m pip install -r requirements.txt"
}

Write-Host "=== Kumsa Moroda test ==="
Write-Host "Storyboard: $sb"
Write-Host ""

Write-Host "[1/6] Validate..."
& $py -m pipeline.script --validate-only --storyboard $sb

Write-Host "[2/6] Narration..."
& $py -m pipeline.narration --storyboard $sb

Write-Host "[3/6] Keyframes..."
& $py -m pipeline.keyframes --storyboard $sb

Write-Host "[4/6] Shots..."
& $py -m pipeline.shots --storyboard $sb

Write-Host "[5/6] Music..."
& $py -m pipeline.music --storyboard $sb

Write-Host "[6/6] Assemble..."
& $py -m pipeline.assemble --storyboard $sb

Write-Host ""
Write-Host "Done."
Write-Host "  outputs/film/final_9x16.mp4"
Write-Host "  outputs/film/final_16x9.mp4"
