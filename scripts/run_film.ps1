# One-command film build for Windows (no Make required)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PYTHONPATH = (Get-Location).Path
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { throw "Create venv first: py -3 -m venv .venv && .\.venv\Scripts\python -m pip install -r requirements.txt" }

& $py -m pipeline.script --validate-only
& $py -m pipeline.narration
& $py -m pipeline.keyframes
& $py -m pipeline.shots
& $py -m pipeline.music
& $py -m pipeline.assemble
Write-Host "Done. See outputs/film/final_9x16.mp4 and final_16x9.mp4"
