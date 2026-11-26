# Personal film: The Summer I Discovered Another World
# Amharic narration + Amharic captions; native 9:16 and 16:9
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PYTHONPATH = (Get-Location).Path
$py = ".\.venv\Scripts\python.exe"
$sb = (Resolve-Path ".\storyboards\wallaga_summer.json").Path

if (-not (Test-Path $py)) {
  throw "Create venv first: py -3 -m venv .venv; .\.venv\Scripts\python -m pip install -r requirements.txt"
}

Write-Host "=== The Summer I Discovered Another World ==="
Write-Host "Storyboard: $sb"
Write-Host "Narration/captions: Amharic only"
Write-Host ""

& $py -m pipeline.script --validate-only --storyboard $sb
if ($LASTEXITCODE -ne 0) { throw "validate failed" }

& $py -m pipeline.narration --storyboard $sb --force
if ($LASTEXITCODE -ne 0) { throw "narration failed" }

& $py -m pipeline.keyframes --storyboard $sb --force
if ($LASTEXITCODE -ne 0) { throw "keyframes failed" }

& $py -m pipeline.shots --storyboard $sb --force
if ($LASTEXITCODE -ne 0) { throw "shots failed" }

& $py -m pipeline.music --storyboard $sb --force
if ($LASTEXITCODE -ne 0) { throw "music failed" }

& $py -m pipeline.assemble --storyboard $sb
if ($LASTEXITCODE -ne 0) { throw "assemble failed" }

Write-Host ""
Write-Host "Done."
Write-Host "  outputs/film/final_9x16.mp4"
Write-Host "  outputs/film/final_16x9.mp4"
Write-Host "  outputs/subs/am.srt"
