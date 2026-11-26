# Failures

| What broke | What we tried | What fixed it / workaround |
|------------|---------------|----------------------------|
| `gemini-2.0-flash` 404 NOT_FOUND | Job failed at script stage | Switched to Gemini 3.x model ids (`gemini-3.5-flash-lite` default) |
| `gemini-3.8-flash` 503 high demand | Script stage unavailable | Fallback chain in `config.py`; prefer Flash-Lite for bulk |
| Film looked like captions on black; silent audio | Cached Pillow placeholders + silent WAV; Cloudflare `seed` 400; old TTS `speechConfig` API | FLUX without seed; Gemini Interactions TTS API; force-regenerate; fix mix label `[voice]` |
| FFmpeg not on PATH (Windows) | winget / Scoop stalled | `imageio-ffmpeg` via `config.ffmpeg_exe()` |
| No GEMINI / Cloudflare keys early | Stages with placeholders | Silent WAV, Pillow keyframes, procedural music — assembly still developable |
| Wan GPU clips not available locally | Backend chain `wan → hunyuan → kenburns` | Default Ken Burns; drop Wan exports into `outputs/shots/external/` |
| ACE-Step not run on local CPU | Looked for candidates folder | Procedural instrumental bed from `music.caption`; notebooks path for Kaggle ACE-Step |
| Afaan Oromo narration hang | Long TTS wait / stuck job on Oromo lines | Kill job; rewrite storyboard to English; document as language ceiling failure |
| Storyboard vs outputs drift | `storyboard.json` updated to Wallaga while film/subs still Kumsa | Force regenerate narration → keyframes → shots → music → assemble from current contract |
| Railway worker “no start command” / bad `${PORT}` | Railpack / Procfile / railway.toml variants | Moved worker to Render Docker (`Dockerfile` + `render.yaml`) |
| Web UI showed `Error [object Object]` | FastAPI `detail` object passed to `Error()` | `formatError` in web lib + stringify in jobs API |
| Script validation: Gemini returned music without `caption` | Schema required `caption` + `duration_sec` | `normalize_storyboard` fills `caption`; hand-authored `storyboard.json` remains source of truth for showcase |
| Script validation: Gemini `end_card` as `{title, subtitle}` (sometimes `duration_sec` > 5) | Schema requires `{text, duration_sec}` 1–5 | `normalize_end_card` in `pipeline/common.py`; always runs inside `validate_storyboard` |
| Deploy Quick Test: `storyline` &lt; 20 chars | Older worker `min_length=20` | Vercel sends embedded `DEMO_STORYBOARD` + ≥20-char `DEMO_STORYLINE`; worker accepts `demo=true` first |
| Deploy Quick Test: `shots` minItems (1 shot vs schema 6) | Stale worker schema still had `minItems: 6` | Demo board now has 6×3s shots; `normalize_storyboard` pads thin boards to 6; validate relaxes `minItems` to 1 |
| Gemini TTS 429 / quota on deploy | Interactions TTS path flaky under free tier | Edge TTS male English fallback in narration stage |
| Vercel alone cannot run FFmpeg pipeline | Assumed serverless film gen | Split: Vercel UI + remote worker (`WORKER_URL` / `WORKER_SECRET`) |
