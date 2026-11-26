# GPU notebooks (Wan + ACE-Step)

The brief’s free GPU path. Local `make film` defaults to Ken Burns + procedural music so a clean clone still finishes; use these notebooks when you have Kaggle/Colab quota.

## Wan 2.2 TI2V-5B (moving shots)

1. Phone-verify Kaggle; open a GPU notebook (2× T4).
2. Load Wan 2.2 TI2V-5B (see model card: https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B).
3. Upload `outputs/keyframes/shot_XX.png` and the shot’s `motion_prompt` from `storyboard.json` (motion/camera only).
4. Draft at 480p if quota is tight; finish chosen shots at 720p.
5. Export `shot_XX_wan.mp4` into `outputs/shots/external/`.
6. `make shots` then `make film` — external clips win over Ken Burns.
7. Log wall time and GPU minutes in `COSTS.md`; failures in `FAILURES.md`.

## ACE-Step 1.5 (score)

1. Use storyboard `music.caption`, `tempo_bpm`, `duration_sec`, `instrumental: true`.
2. Generate **three** candidates; listen under narration at low volume.
3. Drop the chosen `.wav` (and optionally runners-up) into `outputs/music/candidates/`.
4. `make music` then `make film`.
5. Record why you picked the winner in `EXPERIMENTS.md`.

## Why Ken Burns / procedural bed may still be in the submitted film

GPU queue, session timeouts, or time-to-deadline. The brief allows animating keyframes with pan-zoom and still counting a narrated, scored, subtitled sequence as a film. Prefer Wan/ACE-Step when quota allows; keep fallbacks so `make film` never hard-depends on a live GPU.
