# The Heritage Short — video generator

One-command pipeline that turns `storyboard.json` into a 60–90s heritage short (vertical + horizontal), plus a small web app to paste a storyline and download a film.

## One command

```bash
# Python 3.11+, FFmpeg on PATH
py -3 -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # add GEMINI_API_KEY, Cloudflare keys

# Windows (no Make):
powershell -File scripts/run_film.ps1

# Or with Make:
make film
```

Outputs:

- `outputs/film/final_9x16.mp4`
- `outputs/film/final_16x9.mp4`

Without API keys the pipeline still runs using placeholders (silent narration, drawn keyframes, procedural music, Ken Burns motion) so you can verify assembly.

## Stages

| Stage | Command | Model / tool |
|-------|---------|--------------|
| Validate / script | `make validate` / `python -m pipeline.script` | Gemini Flash |
| Narration | `make narration` | Gemini TTS (or silent placeholder) |
| Keyframes | `make keyframes` | FLUX on Cloudflare (or Pillow placeholder) |
| Shots | `make shots` | Wan → Hunyuan → **Ken Burns** (default) |
| Music | `make music` | ACE-Step export or procedural bed |
| Assemble | `make film` | FFmpeg (duck, subs, loudnorm, end card) |

Switch motion backend:

```bash
# .env
SHOT_BACKEND=kenburns   # or wan | hunyuan
```

Drop Wan clips into `outputs/shots/external/{shot_id}_wan.mp4` after Kaggle runs; ACE-Step wavs into `outputs/music/candidates/`.

## Radio cut (Phase 1)

```bash
make radio
```

## Web app (Vercel + worker)

Vercel hosts the UI only. Film generation needs the Python worker (FFmpeg + Gemini + Cloudflare) on Railway or Render.

### Local

```bash
make web-install
make web-dev          # Next.js on :3000
make worker           # FastAPI worker on :8080
```

`web/.env.local`:

```env
WORKER_URL=http://127.0.0.1:8080
WORKER_SECRET=change-me
```

Root `.env` (worker): `GEMINI_API_KEY`, Cloudflare keys, same `WORKER_SECRET`.

### Deploy

1. **Worker (Railway)** — deploy from **repo root** (not `web/`).
   - Start command must be `python main.py` (do **not** put `${PORT:-8080}` in the Railway UI — clear any Custom Start Command so `railpack.json` / `Procfile` apply).
   - Install/system: FFmpeg must be available (Dockerfile already installs it).
   - Env vars: `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_TTS_MODEL`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, `WORKER_SECRET`, `SHOT_BACKEND=kenburns`, `PYTHONPATH=/app` (or `.` for Railpack).
   - Note the public URL (e.g. `https://….up.railway.app`).
2. **Web (Vercel)** — import the GitHub repo, set **Root Directory** to `web`, then env:
   - `WORKER_URL` = that Railway URL (no trailing slash)
   - `WORKER_SECRET` = same secret as the worker  
   Redeploy after saving env vars.
3. Open the Vercel URL → paste a storyline → download when `ready`.

If Vercel still says it cannot reach the worker, `WORKER_URL` is wrong or still set to localhost.

## Costs

Free-tier oriented. Measured latency and GPU minutes live in `COSTS.md` and `runs.jsonl`.

## Docs

- `DESIGN.md` — audience, intent, user tests  
- `ARCHITECTURE.md` — stages, caching, failure handling  
- `EXPERIMENTS.md` — hypothesis → change → result  
- `FAILURES.md` — blockers and fixes  
- `COSTS.md` — latency / cost notes  
- `ETHICS.md` — consent, licences, labelling  
