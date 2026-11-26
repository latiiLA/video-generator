# Failures

| What broke | What we tried | What fixed it / workaround |
|------------|---------------|----------------------------|
| FFmpeg not on PATH (Windows) | winget + direct GitHub zip (slow/failed); Scoop download stalled (~1MB of 72MB) | Keep Scoop install running or install FFmpeg manually; shots/assemble require it |
| No GEMINI / Cloudflare keys yet | Ran stages with placeholders | Silent WAV narration, Pillow keyframes, procedural music bed — assembly still works once FFmpeg is present |
| Wan GPU clips not available locally | Backend chain `wan → hunyuan → kenburns` | Default `SHOT_BACKEND=kenburns`; drop exports into `outputs/shots/external/` |

Add real blockers (quota, OOM, TTS pronunciation, Cloudflare daily cap) as they appear.
