# Experiments

Hypothesis → change → result. Evidence in `runs.jsonl` unless noted.

| # | Hypothesis | Change | Result |
|---|------------|--------|--------|
| 1 | Radio cut first catches pacing cheaper than regenerating images | Built `make radio` (narration + music + black) before committing to Wan | True — story/language issues found before GPU spend; radio path is the Phase 1 checkpoint |
| 2 | Fixed `style_block` + reference sheet reduces character drift | `pipeline/keyframes.py` generates `outputs/references/character.png` then appends style/character to every prompt | Improved recognisable “same world”; faces still drift without LoRA — acceptable for floor |
| 3 | Ken Burns is a valid film when Wan quota/GPU unavailable | Default `SHOT_BACKEND=kenburns` with Wan/Hunyuan override + `outputs/shots/external/` drop-in | True — full dual-aspect film assembles; brief explicitly allows pan-zoom fallback |
| 4 | Motion-only I2V prompts beat re-describing the scene | Storyboard `motion_prompt` is camera/action only; image holds subject | Used for Ken Burns directions; ready for Wan when clips land |
| 5 | Three music candidates beat one-shot generation | ACE-Step via `outputs/music/candidates/`; else procedural bed from caption | Procedural bed used when no candidates present (`music/procedural-bed` in logs); audition path documented in notebooks/ |
| 6 | Ducking threshold 0.02 / ratio 6 / attack 300 / release 1500 keeps voice clear | FFmpeg `sidechaincompress` defaults from brief Appendix B | Voice remains spine; music audible in gaps — kept |
| 7 | Own-language TTS needs a native listen before picture spend | Attempted Afaan Oromo lines + Gemini TTS | Failed practically (hang / unusable wait) — recorded in FAILURES; switched to English; ceiling experiment documented |
| 8 | Mid-frame subjects survive 9:16 and 16:9 from one master | Centered compositions + assemble crop/letterbox paths | Both exports produced; vertical is primary for phone audience |
| 9 | Content-hash cache regenerates only changed shots | `content_hash` keys under `cache/` per stage | Confirmed: editing one narration line re-TTS only that shot; `--force` bypasses |
| 10 | Web “family tool” ceiling: relative pastes storyline → film | Next.js UI + FastAPI worker (Render) + Ken Burns default | Job create works when worker reachable; `[object Object]` UI bug fixed by stringifying FastAPI `detail` |
| 11 | Gemini 3.8 Flash may 503 on free tier; lite models keep pipeline alive | Fallback chain `3.5-flash-lite → … → 3.8-flash`; TTS `3.8-flash-lite-tts` | Script/TTS recovered after 404/503 on older ids — see FAILURES |
| 12 | Cloudflare FLUX rejects `seed` on this Workers AI route | Drop seed from request body; keep storyboard seed for logging/cache key only | Keyframes succeed (`flux-1-schnell` ~2.9s median) |
