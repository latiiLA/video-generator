# Failures

| What broke | What we tried | What fixed it / workaround |
|------------|---------------|----------------------------|
| `gemini-2.0-flash` 404 NOT_FOUND | Job failed at script stage | Switched to Gemini 3.x model ids |
| `gemini-3.8-flash` 503 high demand | Script stage unavailable | Default to `gemini-3.5-flash-lite` with auto-fallback chain; TTS uses `gemini-3.8-flash-lite-tts` |
| Film looked like captions on black; silent audio | Cached Pillow placeholders + silent WAV; Cloudflare `seed` 400; old TTS `speechConfig` API | FLUX without seed; Gemini Interactions TTS API; force-regenerate keyframes/narration; fix mix label `[voice]` |
| FFmpeg not on PATH (Windows) | winget + direct GitHub zip (slow/failed); Scoop download stalled (~1MB of 72MB) | Use `imageio-ffmpeg` bundle via `config.ffmpeg_exe()` |
| No GEMINI / Cloudflare keys yet | Ran stages with placeholders | Silent WAV narration, Pillow keyframes, procedural music bed — assembly still works once FFmpeg is present |
| Wan GPU clips not available locally | Backend chain `wan → hunyuan → kenburns` | Default `SHOT_BACKEND=kenburns`; drop exports into `outputs/shots/external/` |

Add real blockers (quota, OOM, TTS pronunciation, Cloudflare daily cap) as they appear.
