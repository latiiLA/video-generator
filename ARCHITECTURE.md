# Architecture

## Contract

`storyboard.json` is the only contract between stages. It is validated against `schema/storyboard.schema.json` before runs.

## Stages

```text
script → narration → keyframes → shots → music → assemble
```

Each stage:

1. Reads the storyboard  
2. Writes only its outputs under `outputs/`  
3. Appends one JSON line per model call to `runs.jsonl`  
4. Skips work when an input-content hash already exists in `cache/`

## Caching

`pipeline/common.py` hashes stage inputs (prompts, seeds, backend, file fingerprints). Re-running after editing one shot regenerates only that shot’s dependent artifacts.

## Backend switching

Env vars (see `.env.example`):

- `SHOT_BACKEND=wan|hunyuan|kenburns` — tried in order with automatic fallback to Ken Burns  
- `IMAGE_BACKEND`, `TTS_BACKEND`, `MUSIC_BACKEND`

Per-shot override: `shots[].shot_backend`.

## Failure handling

- Retries (tenacity) on transient API errors  
- Missing API keys → explicit placeholders so assembly can still be developed  
- Missing Wan/Hunyuan GPU exports → Ken Burns  
- Missing ACE-Step candidates → procedural music bed  
- Failures logged with `success: false` in `runs.jsonl` and narrative in `FAILURES.md`

## Web product

- **Vercel (`web/`):** UI + thin API that forwards jobs to the worker  
- **Worker (`pipeline/worker.py`):** FastAPI; runs the same Python stages; serves MP4s  
- Vercel does **not** run FFmpeg or GPU jobs
