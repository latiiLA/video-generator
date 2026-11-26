# The Heritage Short — video generator

**Made by Lata Amenu** · 10 Academy · B2W0 Challenge

One-command pipeline that turns `storyboard.json` into a 60–90s heritage short (vertical + horizontal), plus a showcase web app to watch the film, paste a storyline, and run a Quick Test.

Film: *The Summer I Discovered Another World* (Wallaga childhood summer). Authorship, implementation map, and evidence: **`CONTRIBUTIONS.md`**.

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
| Narration | `make narration` | Gemini TTS → Edge TTS (or silent placeholder) |
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

### Deploy (recommended: Render + Vercel)

1. **Worker on Render** (Docker — avoids Railway Railpack issues)
   - Go to [render.com](https://render.com) → **New** → **Blueprint** (uses `render.yaml`) **or** **Web Service** → connect `latiiLA/video-generator`
   - Runtime: **Docker**, Dockerfile path `./Dockerfile`, root directory `/`
   - Set env vars (same as local root `.env`):
     - `GEMINI_API_KEY`
     - `CLOUDFLARE_ACCOUNT_ID`
     - `CLOUDFLARE_API_TOKEN`
     - `WORKER_SECRET` (pick a strong value)
     - optional: `SHOT_BACKEND=kenburns`
   - After deploy, open `https://YOUR-SERVICE.onrender.com/health` → should show `{"status":"ok"}`
2. **Web on Vercel** — Root Directory = `web`, env:
   - `WORKER_URL=https://YOUR-SERVICE.onrender.com` (no trailing slash)
   - `WORKER_SECRET=` same as Render  
   Redeploy Vercel after saving.
3. Generate a film on the Vercel URL.

Note: free Render services spin down after idle; the first request may take ~30–60s to wake.

## Costs

Free-tier oriented. Measured latency and GPU minutes live in `COSTS.md` and `runs.jsonl`.

## Docs

- `CONTRIBUTIONS.md` — authorship, what was built, evidence map  
- `ARCHITECTURE.md` — stages, caching, web/worker deploy topology  
- `DESIGN.md` — audience, intent, chronology, user tests  
- `REPORT.md` — assignment narrative (hardest problem, ceiling, next steps)  
- `EXPERIMENTS.md` — hypothesis → change → result  
- `FAILURES.md` — blockers and fixes  
- `COSTS.md` — latency / cost notes  
- `ETHICS.md` — consent, licences, labelling  
