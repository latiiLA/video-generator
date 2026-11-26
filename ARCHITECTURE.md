# Architecture

## Contract

`storyboard.json` is the only contract between stages. It is validated against `schema/storyboard.schema.json` before runs.

Before validation, `pipeline/common.py` runs **`normalize_storyboard`**, which repairs common Gemini mistakes (especially `end_card` as `{title, subtitle}` → `{text, duration_sec}`, and music missing `caption`).

Active creative contract for the showcase film: `storyboards/wallaga_summer.json` (copied/synced to `storyboard.json`). Quick Test uses `storyboards/demo_5s.json` / embedded `web/lib/demoStoryboard.ts`.

## Stages

```text
script → narration → keyframes → shots → music → assemble
                 ↘ radio cut (narration + music + black picture)
```

| Stage | Module | Typical backend |
|-------|--------|-----------------|
| Script | `pipeline/script.py` | Gemini JSON storyboard (or pasted / demo board) |
| Narration | `pipeline/narration.py` | Gemini TTS → Edge TTS male EN fallback → silent WAV |
| Keyframes | `pipeline/keyframes.py` | Cloudflare FLUX → Pillow placeholder |
| Shots | `pipeline/shots.py` | Wan → Hunyuan → **Ken Burns** (default) |
| Music | `pipeline/music.py` | ACE-Step candidates → procedural bed |
| Assemble | `pipeline/assemble.py` | FFmpeg: duck, Amharic/EN subs, loudnorm, end card, **native 16:9 + 9:16** |

Each stage:

1. Reads the storyboard  
2. Writes only its outputs under `outputs/` (per-job under `outputs/jobs/{id}/` for the worker)  
3. Appends one JSON line per model call to `runs.jsonl`  
4. Skips work when an input-content hash already exists in `cache/`

## Caching

`pipeline/common.py` hashes stage inputs (prompts, seeds, backend, file fingerprints). Re-running after editing one shot regenerates only that shot’s dependent artifacts. Use `--force` / stage flags to bypass.

## Backend switching

Env vars (see `.env.example`):

- `SHOT_BACKEND=wan|hunyuan|kenburns` — tried in order with automatic fallback to Ken Burns  
- `IMAGE_BACKEND`, `TTS_BACKEND`, `MUSIC_BACKEND`

Per-shot override: `shots[].shot_backend`.

## Failure handling

- Retries (tenacity) on transient API errors  
- Gemini model fallback chain in `config.py`  
- Missing API keys → explicit placeholders so assembly can still be developed  
- Missing Wan/Hunyuan GPU exports → Ken Burns  
- Missing ACE-Step candidates → procedural music bed  
- Storyboard shape drift from Gemini → normalize then validate  
- Failures logged with `success: false` in `runs.jsonl` and narrative in `FAILURES.md`

## Web product

```text
Browser → Vercel Next.js (web/) → POST /api/jobs → Render FastAPI worker
                                      ↓
                              pipeline stages + FFmpeg
                                      ↓
                              GET job status / MP4 URLs
```

- **Vercel (`web/`):** showcase UI (Film tab with Drive 16:9 then 9:16), Generate, Quick Test (`demo: true`), progress stages  
- **Worker (`pipeline/worker.py`):** FastAPI; auth via `X-Worker-Secret`; runs the same Python stages; serves MP4s  
- **Vercel does not run FFmpeg or GPU jobs** — `WORKER_URL` + `WORKER_SECRET` are required for Generate  

## Deploy topology

| Service | Host | Artifact |
|---------|------|----------|
| UI | Vercel (root `web/`) | Next.js |
| Worker | Render (Docker) | `Dockerfile` + `render.yaml` |

See `README.md` for env vars and `CONTRIBUTIONS.md` for authorship / evidence map.
