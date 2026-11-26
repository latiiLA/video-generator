# Report — The Heritage Short (Summer in the Gojo)

*Submit this as PDF/Word or link for Assignment 1. Edit the bracketed bits after your two audience tests.*

## What I set out to make, and for whom

A 60–90s film about one summer at my grandfather’s place in rural Wallaga: firelight in a gojo without electricity, mitmita potatoes, uncles on the land, a first horse, rain, and the ache that family lives far away. Audience: relatives who share that world, and friends who only know city life, watching on a phone. Intent: feel how precious those days were, and that memory keeps them near.

## What I learned from the audience

**Radio cut:** [Paste DESIGN.md User test 1 — what ≥3 people said and what you changed in storyboard.json.]

**Near-final cut:** [Paste DESIGN.md User test 2 — what ≥3 people said and what changed.]

Pre-audience iteration already in the repo: the first draft subject (public history) was replaced by this personal chronology so the film is for family, not a lecture.

## Hardest problem and how I solved it

Keeping a reproducible multi-model pipeline running on free tiers when models, hosts, and APIs moved under us: Gemini model id 404s and 503s, Cloudflare FLUX rejecting `seed`, TTS API shape changes, Windows FFmpeg PATH, Railway failing to start the worker, and a web UI that rendered FastAPI errors as `[object Object]`. Fixes live in `FAILURES.md` and `runs.jsonl`: model fallback chains, Interactions TTS, Ken Burns as the honest motion floor, Render Docker for the worker, and proper error stringification.

## Suggested practice that beat my instinct

**Radio cut / narration-first.** Instinct was to generate pictures early. Timing the voice first (`make radio`) and treating `storyboard.json` as the only contract caught language and pacing issues before spending image quota — exactly as the brief suggested.

## Suggested practice that did not beat my instinct

**Own-language narration as the default first film.** Instinct and the brief both push Afaan Oromo; Gemini TTS is listed with broad language support. In practice the Oromo path hung / was unusable under our free-tier calls, so English shipped for the deadline film and the Oromo attempt is documented as a ceiling/failure experiment rather than a silent retreat.

## Ceiling work

1. **Family tool:** a small web app (`web/`) so a relative can paste a storyline and get a film back via a remote worker — not only a CLI.
2. **Language probe:** Afaan Oromo attempted and measured as failure modes in FAILURES.md.
3. **Deploy path:** Vercel UI + Render worker when “one machine” was not enough for the showcase.

## What I would build next

Wire real Wan 2.2 and ACE-Step candidate batches from Kaggle into `outputs/shots/external/` and `outputs/music/candidates/`, re-run Oromo with shorter lines and a native listener, and add a blind preference test (Ken Burns vs Wan) with five viewers.

## Evidence map

| Claim | Where |
|-------|--------|
| Stages + cache | `ARCHITECTURE.md`, `pipeline/` |
| One command | `README.md`, `Makefile`, `scripts/run_film.ps1` |
| Logs | `runs.jsonl` |
| Experiments | `EXPERIMENTS.md` |
| Failures | `FAILURES.md` |
| Costs | `COSTS.md` |
| Consent / licences | `ETHICS.md` |
| Audience / tests | `DESIGN.md` |
