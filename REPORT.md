# Assignment 1 Report — The Heritage Short

**Film title:** The Summer I Discovered Another World  
**Author:** Lata Amenu  
**Programme:** 10 Academy · B2W0 Challenge  
**On-film / UI credit:** Made by Lata Amenu  
**Repository:** https://github.com/latiiLA/video-generator  
**Date:** 26 November 2026  

This report accompanies the public codebase. Evidence for each claim is linked in the final evidence map and lives in the repo (`DESIGN.md`, `ARCHITECTURE.md`, `EXPERIMENTS.md`, `FAILURES.md`, `COSTS.md`, `ETHICS.md`, `CONTRIBUTIONS.md`, `runs.jsonl`).

---

## 1. What I set out to make, and for whom

I set out to make a **60–90 second heritage short** about one Grade Seven summer at my grandfather’s place in rural Wallaga: endless greenery, summer rain, work on the land, firelight in a gojo, potatoes cooking, fresh milk, and the ache that ordinary days become memory.

**Audience.** Relatives who already know that countryside world, and friends who grew up only in city life—people watching primarily on a **phone (9:16)**, with a horizontal **16:9** cut for wider sharing.

**Intent.** Feel how precious that “simple visit” was, and understand that the most beautiful journeys can be the ones that take us back to where we first learned to see.

**Contract.** The film is driven by a validated `storyboard.json` (active creative source: `storyboards/wallaga_summer.json`), not by ad-hoc prompts. A first draft that used public history (Kumsa Moroda) was deliberately replaced so the film would be **for family**, not a lecture. That separation is documented in `DESIGN.md` and kept as `storyboards/kumsa_moroda.json` for contrast only.

**Shipped language path.** English male narration (stock TTS, not a relative’s voice) with **Amharic burned-in captions**, dual-aspect export, ducked score, and an AI-labelled end card.

---

## 2. What I learned from the audience

### Design pivot before formal picture spend

Early feedback on the public-history draft was that it felt like a lecture. I replaced it with the personal Wallaga chronology (nine shots, each with an explicit *reason* in the storyboard). That change taught me the brief’s audience/intent gate is not optional: if the first viewer cannot feel *who it is for*, no amount of pipeline polish saves the film.

### User test 1 — radio cut (narration-first)

- **Prototype:** narration + music path / radio-style listen (`make radio` / early VO assembly) before committing image quota.  
- **Participants (≥3):** three listeners drawn from classmates and family familiar with either countryside or city-only childhoods.  
- **What they said:**  
  - The opening “I thought it was only a visit” lands; keep it.  
  - Gojo night and fresh milk are the emotional centre—don’t rush them.  
  - Own-language (Afaan Oromo) attempt was hard to follow / unreliable in our TTS path; English VO was clearer for mixed listeners.  
  - Amharic text on screen helps relatives who follow the story better in writing than in English audio.  
- **What I changed in `storyboard.json`:** locked the nine-beat personal chronology; kept English narration lines as the spine; set Amharic caption fields as the burned-in subtitle language; preserved longer emotional beats on gojo and milk rather than trimming them for speed.

### User test 2 — near-final cut

- **Prototype:** `outputs/film/final_9x16.mp4` (and matching 16:9).  
- **Participants (≥3):** three viewers (phone-first watch for vertical; one desktop watch for horizontal).  
- **What they said:**  
  - Vertical feels right for the phone audience; horizontal is useful for sharing.  
  - Faces must read as Horn of Africa / Ethiopian—not a generic “global South” look.  
  - Motion can be gentle (Ken Burns); the voice and captions carry the film.  
  - End card / “Made with AI” labelling is expected and fine; credit “Made by Lata Amenu” matters on the showcase.  
- **What I changed:** strengthened Ethiopian facial descriptors in `style_block` and shot prompts; kept Ken Burns as the honest default motion floor; shipped dual native aspects; wired the showcase Film tab to Drive cuts (16:9 then 9:16) with author credit in the UI.

---

## 3. Hardest problem and how I solved it

The hardest problem was keeping a **reproducible multi-model pipeline** alive on **free tiers** while APIs, model IDs, and hosts moved under us—and then making the same pipeline reachable from a deployed web UI.

Concrete failures (full table in `FAILURES.md`):

| Failure class | What broke | Fix |
|---------------|------------|-----|
| Model IDs | Gemini 404 / 503 on free tier | Fallback chain in `pipeline/config.py` (Flash-Lite first) |
| Image API | Cloudflare FLUX rejecting `seed` | Drop seed from request; keep seed for cache keys only |
| TTS | API shape changes + 429 quota | Interactions TTS path, then **Edge TTS male EN** fallback |
| Local tooling | FFmpeg missing on Windows PATH | `imageio-ffmpeg` via `config.ffmpeg_exe()` |
| Motion / music GPU | No local Wan / ACE-Step | Ken Burns + procedural bed; Kaggle drop-in folders documented |
| Hosting | Railway start / `${PORT}` pain | **Render Docker** worker (`Dockerfile`, `render.yaml`) |
| Web errors | FastAPI `detail` shown as `[object Object]` | `formatError` stringification in the Next.js jobs API |
| Schema drift | Gemini `end_card` as `{title, subtitle}`; demo `shots` too few for stale `minItems: 6` | `normalize_end_card` / `normalize_storyboard` inside `validate_storyboard`; 6-shot Quick Test board from Vercel |

Evidence: `FAILURES.md`, `runs.jsonl`, `pipeline/common.py`, `web/lib/demoStoryboard.ts`.

---

## 4. Suggested practice that beat my instinct

**Radio cut / narration-first.**

My instinct was to generate pictures early so the project would “look like a film.” The brief’s radio-cut practice beat that instinct. Timing the voice first (`make radio`) and treating **`storyboard.json` as the only contract** caught language, pacing, and story-subject problems *before* spending FLUX quota or motion time. Every later stage only reads the storyboard and writes its own outputs under `outputs/`, with content-hash caching so one changed line does not rebuild the world (`ARCHITECTURE.md`, experiment #1 and #9 in `EXPERIMENTS.md`).

---

## 5. Suggested practice that did not beat my instinct

**Own-language narration as the default first ship.**

Instinct and the brief both push heritage language (Afaan Oromo). Gemini TTS is advertised with broad language support, so I tried Oromo lines early. In practice the path **hung / became unusable** under our free-tier calls (documented in `FAILURES.md` and experiment #7). For the deadline film I shipped **English male VO + Amharic captions**, and kept the Oromo attempt as an honest ceiling/failure experiment rather than silently pretending the first film was Oromo-narrated. That was the right engineering call and the right ethics call: do not fake a language path that did not actually run.

---

## 6. Ceiling work

Beyond the floor pipeline I shipped:

1. **Family / showcase web app (`web/`)** — Film tab (Drive 16:9 + 9:16), Generate from storyline, Quick Test, live stage progress — not only a CLI.  
2. **Deploy split** — Vercel UI + Render Docker worker, because Vercel cannot run FFmpeg.  
3. **Dual native aspects** — true 16:9 and 9:16 assemble paths.  
4. **Language path** — English VO + Amharic captions; Oromo TTS measured as failure.  
5. **Deploy hardening** — storyboard normalization, Quick Test embedded board, worker `demo=true` path.

Authorship and file map: `CONTRIBUTIONS.md`.

---

## 7. What I would build next

1. Batch real **Wan 2.2** clips and **ACE-Step** music candidates from Kaggle into `outputs/shots/external/` and `outputs/music/candidates/`, then re-assemble.  
2. Retry **Afaan Oromo** with shorter lines and a native listener *before* picture spend.  
3. Run a **blind preference test** (Ken Burns vs Wan) with five viewers and append the row to `EXPERIMENTS.md`.  
4. If an organisation frontier lane opens (Omni Flash / Lyria-class tools), compare one shot blind and record cost/latency in `COSTS.md`.

---

## 8. Evidence map

| Claim | Where in the repo |
|-------|-------------------|
| Audience, intent, chronology, user tests | `DESIGN.md` |
| Stages, cache, web/worker topology | `ARCHITECTURE.md` |
| ≥10 experiments with results | `EXPERIMENTS.md` |
| Failures and fixes | `FAILURES.md` |
| Measured latency / $0 free-tier path | `COSTS.md`, `runs.jsonl` |
| Consent, licences, AI labelling | `ETHICS.md` |
| Authorship / what I built | `CONTRIBUTIONS.md` |
| One command | `README.md`, `Makefile`, `scripts/run_film.ps1` |
| Storyboard contract + schema | `storyboard.json`, `schema/storyboard.schema.json`, `storyboards/wallaga_summer.json` |
| Pipeline implementation | `pipeline/` |
| Web + worker | `web/`, `pipeline/worker.py`, `Dockerfile`, `render.yaml` |
| Showcase film links | `web/lib/film.ts` (Drive 16:9 + 9:16) |

---

## 9. Ethics summary (for graders)

- Stylized AI imagery; **no** photoreal clones of named relatives; **no** voice clone.  
- End card / platform labelling: Made with AI; author credit Made by Lata Amenu.  
- Private identifiers kept out of free endpoints that may train on inputs.  

Full table: `ETHICS.md`.

---

## 10. How to reproduce

```bash
# Clone, Python 3.11+, FFmpeg available (or imageio-ffmpeg)
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
copy .env.example .env         # add GEMINI_API_KEY, Cloudflare keys

powershell -File scripts/run_film.ps1
# → outputs/film/final_9x16.mp4
# → outputs/film/final_16x9.mp4
```

Web locally: `make web-dev` + `make worker` (see `README.md`).

---

*End of Assignment 1 report — Lata Amenu.*
