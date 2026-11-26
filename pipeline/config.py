"""Environment-driven backend selection."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", ROOT / "outputs"))
RUNS_LOG = Path(os.getenv("RUNS_LOG", ROOT / "runs.jsonl"))
STORYBOARD_PATH = ROOT / "storyboard.json"
SCHEMA_PATH = ROOT / "schema" / "storyboard.schema.json"
CACHE_DIR = ROOT / "cache"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
IMAGE_MODEL = os.getenv(
    "IMAGE_MODEL", "@cf/black-forest-labs/flux-1-schnell"
)

SHOT_BACKEND = os.getenv("SHOT_BACKEND", "kenburns").lower()
IMAGE_BACKEND = os.getenv("IMAGE_BACKEND", "flux").lower()
TTS_BACKEND = os.getenv("TTS_BACKEND", "gemini").lower()
MUSIC_BACKEND = os.getenv("MUSIC_BACKEND", "acestep").lower()

WORKER_SECRET = os.getenv("WORKER_SECRET", "change-me")
SHOT_FALLBACKS = ["wan", "hunyuan", "kenburns"]
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "")


def ffmpeg_exe() -> str:
    """Prefer PATH, then FFMPEG_BIN, then imageio-ffmpeg bundle."""
    import shutil

    if FFMPEG_BIN and Path(FFMPEG_BIN).exists():
        return FFMPEG_BIN
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "ffmpeg not found. Install FFmpeg or: pip install imageio-ffmpeg"
        ) from exc


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for sub in (
        "references",
        "keyframes",
        "shots",
        "narration",
        "music",
        "subs",
        "film",
        "jobs",
    ):
        (OUTPUT_DIR / sub).mkdir(parents=True, exist_ok=True)
