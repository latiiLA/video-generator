# Report — The Heritage Short (The Summer I Discovered Another World)

**Author:** Lata Amenu · **Credit:** Made by Lata Amenu  
*Submit this as PDF/Word or link for Assignment 1. Edit the bracketed bits after your two audience tests. Full implementation map: `CONTRIBUTIONS.md`.*

## What I set out to make, and for whom

A 60–90s film about one summer at my grandfather’s place in rural Wallaga: firelight in a gojo without electricity, potatoes cooking, uncles on the land, summer rain, fresh milk, and the feeling that ordinary days become memory. Audience: relatives who share that world, and friends who only know city life, watching on a phone. Intent: feel how precious those days were, and that the most beautiful journeys can be the ones that take us back.

## What I learned from the audience

**Radio cut:** [Paste DESIGN.md User test 1 — what ≥3 people said and what you changed in storyboard.json.]

**Near-final cut:** [Paste DESIGN.md User test 2 — what ≥3 people said and what changed.]

Pre-audience iteration already in the repo: the first draft subject (public history) was replaced by this personal chronology so the film is for family, not a lecture.

## Hardest problem and how I solved it

Keeping a reproducible multi-model pipeline running on free tiers when models, hosts, and APIs moved under us: Gemini model id 404s and 503s, Cloudflare FLUX rejecting `seed`, TTS API shape / quota changes, Windows FFmpeg PATH, Railway failing to start the worker, a web UI that rendered FastAPI errors as `[object Object]`, and Gemini storyboards that violated our schema (`end_card` as title/subtitle). Fixes live in `FAILURES.md` and `runs.jsonl`: model fallback chains, Edge TTS fallback, Ken Burns as the honest motion floor, Render Docker for the worker, storyboard normalization before validation, and proper error stringification.

## Suggested practice that beat my instinct

**Radio cut / narration-first.** Instinct was to generate pictures early. Timing the voice first (`make radio`) and treating `storyboard.json` as the only contract caught language and pacing issues before spending image quota — exactly as the brief suggested.

## Suggested practice that did not beat my instinct

**Own-language narration as the default first film.** Instinct and the brief both push Afaan Oromo; Gemini TTS is listed with broad language support. In practice the Oromo path hung / was unusable under our free-tier calls, so English shipped for the deadline film and the Oromo attempt is documented as a ceiling/failure experiment rather than a silent retreat.

## Ceiling work

1. **Family / showcase tool:** Next.js app (`web/`) with Film playback (Drive 16:9 + 9:16), Generate from storyline, Quick Test, and live stage progress — not only a CLI.
2. **Language path:** English male VO + Amharic burned-in captions for the shipped film; Afaan Oromo TTS attempted and measured as failure modes in `FAILURES.md`.
3. **Deploy path:** Vercel UI + Render Docker worker when “one machine” was not enough for the showcase.
4. **Dual native aspects:** true 16:9 and 9:16 exports from assemble (not a single master with crude letterbox-only thinking).

## What I would build next

Wire real Wan 2.2 and ACE-Step candidate batches from Kaggle into `outputs/shots/external/` and `outputs/music/candidates/`, re-run Oromo with shorter lines and a native listener, and add a blind preference test (Ken Burns vs Wan) with five viewers.

## Evidence map

| Claim | Where |
|-------|--------|
| Authorship / what I built | `CONTRIBUTIONS.md`, UI credit in `web/lib/film.ts` |
| Stages + cache + deploy topology | `ARCHITECTURE.md`, `pipeline/` |
| One command | `README.md`, `Makefile`, `scripts/run_film.ps1` |
| Story / audience | `DESIGN.md`, `storyboards/wallaga_summer.json` |
| Logs | `runs.jsonl` |
| Experiments | `EXPERIMENTS.md` |
| Failures | `FAILURES.md` |
| Costs | `COSTS.md` |
| Consent / licences | `ETHICS.md` |
| Web + worker | `web/`, `pipeline/worker.py`, `Dockerfile` |
