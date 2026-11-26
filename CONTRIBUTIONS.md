# Contributions & authorship

## Author

**Lata Amenu** — sole author of this assignment project (*The Heritage Short* / *The Summer I Discovered Another World*), for **10 Academy · B2W0 Challenge**.

On-film and UI credit: **Made by Lata Amenu**.

| Area | Contribution |
|------|----------------|
| Story & design | Personal Wallaga summer essay → `storyboards/wallaga_summer.json` as the active film contract (separated from `kumsa_moroda.json`) |
| Pipeline | End-to-end Python stages: script → narration → keyframes → shots → music → assemble |
| Dual-aspect export | Native **16:9** and **9:16** finals via FFmpeg (`outputs/film/final_*.mp4`) |
| Web product | Next.js showcase (`web/`) with Film tab (Drive embeds), Generate, progress, Quick Test |
| Deploy | Vercel UI + Render Docker worker (`Dockerfile`, `render.yaml`) |
| Docs | `DESIGN.md`, `ARCHITECTURE.md`, `EXPERIMENTS.md`, `FAILURES.md`, `COSTS.md`, `ETHICS.md`, `REPORT.md`, this file |
| Evidence | `runs.jsonl`, storyboards, schema, notebooks |

AI coding assistants were used as a **tool** inside this repo (edits, deploys, debugging). Creative ownership of the story, audience intent, ethics choices, and what shipped remains with **Lata Amenu**.

## Implementation map (what lives where)

| Piece | Path | Role |
|-------|------|------|
| Storyboard schema | `schema/storyboard.schema.json` | Contract validation |
| Active storyboard | `storyboard.json` ← `storyboards/wallaga_summer.json` | Film content |
| Demo / Quick Test | `storyboards/demo_5s.json`, `web/lib/demoStoryboard.ts` | ~5s UI smoke job |
| Pipeline stages | `pipeline/*.py` | Model + FFmpeg work |
| Worker API | `pipeline/worker.py` | FastAPI `/jobs`, `/health`, MP4 serve |
| Web UI | `web/app/page.tsx`, `web/lib/film.ts` | Showcase + generate |
| Job proxy | `web/app/api/jobs/` | Forwards to worker with secret |
| One-command film | `Makefile`, `scripts/run_film.ps1` | Local full run |
| Deploy worker | `Dockerfile`, `render.yaml` | Render service |
| Run log | `runs.jsonl` | Latency / success evidence |

## Notable technical choices

1. **`storyboard.json` is the only contract** between stages (see `ARCHITECTURE.md`).
2. **Narration-first / radio cut** before spending image quota (`make radio`).
3. **Ken Burns** as the honest default motion floor when Wan/Hunyuan GPU clips are unavailable.
4. **English male VO + Amharic captions** for the shipped film path (Edge TTS fallback when Gemini TTS quotas fail).
5. **Gemini storyboard repair** — `normalize_storyboard` / `normalize_end_card` in `pipeline/common.py` coerce `title`/`subtitle` end cards and missing music `caption` before schema validation (required for reliable Generate on deploy).
6. **Split hosting** — Vercel cannot run FFmpeg; generation always goes through `WORKER_URL`.

## How to verify contributions in the repo

```bash
# Contract + docs
ls storyboard.json DESIGN.md ARCHITECTURE.md CONTRIBUTIONS.md REPORT.md

# Pipeline one-command (local)
powershell -File scripts/run_film.ps1

# Evidence of model calls
Get-Content runs.jsonl -Tail 20   # or: tail -n 20 runs.jsonl

# Web + worker locally
make web-dev    # :3000
make worker     # :8080
```

Final showcase cuts are also linked from the Film tab via Google Drive IDs in `web/lib/film.ts`.

## Changelog highlights (project arc)

| Milestone | Evidence |
|-----------|----------|
| Multi-stage heritage pipeline + schema | `pipeline/`, `schema/` |
| Wallaga personal film replaces public-history draft | `storyboards/wallaga_summer.json`, `DESIGN.md` |
| Dual-aspect assemble + end card | `pipeline/assemble.py`, film outputs |
| Family / showcase web UI + Quick Test | `web/` |
| Render worker + Vercel proxy | `Dockerfile`, `render.yaml`, `README.md` |
| Deploy hardening: demo storyline ≥20 chars; Gemini `end_card` normalize | `pipeline/common.py`, `web/lib/demoStoryboard.ts`, `FAILURES.md` |
