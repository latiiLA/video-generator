# GPU notebooks

## Wan 2.2 (moving shots)

1. Open a Kaggle notebook with GPU (2× T4).
2. Load Wan 2.2 TI2V-5B.
3. For each keyframe in `outputs/keyframes/shot_XX.png`, generate a short clip with the shot’s `motion_prompt`.
4. Export to `outputs/shots/external/shot_XX_wan.mp4`.
5. Re-run `make shots` (or `make film`). The shots stage will pick up external clips before falling back to Ken Burns.

## ACE-Step 1.5 (music)

1. Generate 3 instrumental candidates from the storyboard `music.caption`.
2. Drop chosen `.wav` files into `outputs/music/candidates/`.
3. Re-run `make music`.

Record latency and GPU minutes in `COSTS.md` and failures in `FAILURES.md`.
