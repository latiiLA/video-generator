# Build Wallaga summer film (Amharic narration + Amharic captions, dual aspect)
Set-Location "C:\Users\lataa\Documents\Projects\video-generator"
$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$py = ".\.venv\Scripts\python.exe"
$sb = (Resolve-Path ".\storyboards\wallaga_summer.json").Path

function Step([string]$name, [scriptblock]$block) {
  Write-Host "=== $name ==="
  & $block
  if ($LASTEXITCODE -ne 0) { throw "Failed: $name exit $LASTEXITCODE" }
}

try {
  Step "validate" { & $py -m pipeline.script --validate-only --storyboard $sb }
  Step "narration" { & $py -m pipeline.narration --storyboard $sb --force }
  Step "keyframes" { & $py -m pipeline.keyframes --storyboard $sb --force }
  Step "shots" { & $py -m pipeline.shots --storyboard $sb --force }
  Step "music" { & $py -m pipeline.music --storyboard $sb --force }
  Step "assemble" { & $py -m pipeline.assemble --storyboard $sb }
  Write-Host "=== DONE ==="
  Get-Item outputs\film\final_9x16.mp4, outputs\film\final_16x9.mp4, outputs\subs\am.srt |
    Select-Object Name, Length, LastWriteTime |
    Format-Table -AutoSize
} catch {
  Write-Host "BUILD FAILED: $_"
  exit 1
}
