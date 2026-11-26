# Costs

Primary path is free-tier oriented (Ethiopia-friendly). Figures below are measured from `runs.jsonl` (96 calls at last summarize).

## Measured (from `runs.jsonl`)

| Stage | Model | Median latency | n (ok) | GPU minutes | List-price equiv |
|-------|-------|----------------|--------|-------------|------------------|
| Smoke / schema | local | ~21 ms | 2 | 0 | $0 |
| Smoke / Gemini | Gemini API | (logged success) | 2 | 0 | $0 free tier |
| Smoke / Cloudflare | Workers AI | (logged success) | 2 | 0 | $0 free allowance |
| Narration | `gemini-3.8-flash-lite-tts` | **~5.3 s** / line | 11 ok / 2 fail | 0 | $0 free tier |
| Keyframes | `@cf/.../flux-1-schnell` | **~2.9 s** / image | 10 | 0 (hosted) | $0 within daily allowance |
| Shots | `ffmpeg-kenburns` | **~0.65 s** / shot | 36 | 0 | $0 |
| Music | `procedural-bed` | **~4.8 s** | 4 | 0 | $0 (ACE-Step GPU would use Kaggle minutes) |
| Assemble | `ffmpeg` | **~14.6 s** | 4 | 0 | $0 |

## GPU path (when used)

| Work | Where | Expected | Notes |
|------|-------|----------|-------|
| Wan 2.2 TI2V-5B ~5s clip | Kaggle 2×T4 | several minutes / clip | Draft 480p; batch; cache by hash |
| ACE-Step 1.5 candidates ×3 | Kaggle/Colab | seconds–minutes / track | Drop wavs into `outputs/music/candidates/` |

Kaggle ~30 GPU hours/week is the binding constraint if you leave Ken Burns.

## Film length target

60–90 s including ~3 s AI end card. Storyboard: 9×~8 s + 3 s ≈ 75 s.

## Frontier comparison (access-limited)

Paid Omni Flash / Nano Banana / Lyria were not available on a personal free key. Floor path = FLUX schnell + Ken Burns + Gemini TTS + procedural/ACE-Step bed. If organisation frontier lane opens, compare one shot blind and append a row here.
