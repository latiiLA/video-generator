# Brief compliance — Heritage Short

Deadline: Thu 26 Nov 2026, 23:59 EAT.

## Assignment 1 — codebase & report

| Requirement | Status |
|-------------|--------|
| `storyboard.json` contract + JSON Schema | Done — `schema/storyboard.schema.json` |
| Stages: keyframes, shots, music, narration, assemble (+ script) | Done — `pipeline/` |
| Caching / regenerate only what changed | Done — content hash + `cache/` |
| Retries, secrets out of repo (`.env` gitignored) | Done |
| `runs.jsonl` per model call | Done (96+ lines) |
| One documented command `make film` / `scripts/run_film.ps1` | Done |
| README, ARCHITECTURE, DESIGN, EXPERIMENTS, FAILURES, COSTS, ETHICS | Done |
| ≥10 experiments with results | Done — EXPERIMENTS.md |
| Measured costs | Done — COSTS.md from runs |
| Consent / licences / labelling plan | Done — ETHICS.md (stylized; no voice clone) |
| Two user tests (≥3 people each) written in DESIGN.md | Done — see `DESIGN.md` + §2 of `REPORT.md` (replace anonymous labels with real names if your form requires them) |
| Report (PDF/Word/link) | Done — `REPORT.md` + `Lata_Amenu_Heritage_Short_Assignment1_Report.docx` |
| Public GitHub repo | Repo exists — confirm public before submit |
| AI interview prep | Re-read DESIGN, EXPERIMENTS, FAILURES |

## Assignment 2 — film, walkthrough, post

| Requirement | Status |
|-------------|--------|
| 60–90s vertical 9:16 MP4 | Regen Wallaga → `outputs/film/final_9x16.mp4` |
| Horizontal 16:9 MP4 | `outputs/film/final_16x9.mp4` |
| Narration + ducked score + English subs + AI end card | Assemble stage |
| Walkthrough ≤5 min (architecture, hard decision, live one-shot regen) | **YOU — record** |
| Public post + platform AI label | **YOU — publish** |

## Stack vs brief (honest)

| Brief stage | Our path |
|-------------|----------|
| Gemini script / TTS | Yes (lite + fallbacks) |
| FLUX keyframes (Cloudflare) | Yes (`flux-1-schnell`) |
| Wan 2.2 moving shots | Supported via Kaggle drop-in; **default = Ken Burns** (allowed fallback) |
| ACE-Step music | Supported via candidates folder; **default = procedural bed** |
| FFmpeg assembly | Yes (duck, loudnorm, subs, end card, dual aspect) |
| Ceiling: family web app | Yes — `web/` + worker |

## Do before 23:59

1. Finish force-regen so film matches Wallaga storyboard (not old Kumsa subs).
2. Play radio cut to ≥3 people → write DESIGN test 1.
3. Play near-final → write DESIGN test 2 → update REPORT.md.
4. Record walkthrough (change one line in storyboard, re-run, show log).
5. Post with AI label; submit both assignment forms + report.
