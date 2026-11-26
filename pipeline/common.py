"""Shared helpers: validation, caching, logging, retries."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TypeVar

import jsonschema
from tenacity import retry, stop_after_attempt, wait_exponential

from pipeline import config

T = TypeVar("T")


def normalize_end_card(end: object) -> dict[str, Any]:
    """Coerce Gemini end_card variants into schema {text, duration_sec}."""
    if isinstance(end, str):
        text = end.strip() or "Made with AI"
        return {"text": text, "duration_sec": 3}
    if not isinstance(end, dict):
        return {"text": "Made with AI", "duration_sec": 3}

    text = (
        end.get("text")
        or end.get("title")
        or end.get("label")
        or end.get("heading")
        or ""
    )
    subtitle = end.get("subtitle") or end.get("tagline") or end.get("call_to_action")
    if isinstance(text, str):
        text = text.strip()
    else:
        text = ""
    if subtitle and isinstance(subtitle, str) and subtitle.strip():
        text = f"{text} · {subtitle.strip()}" if text else subtitle.strip()
    if not text:
        text = "Made with AI"

    raw_dur = end.get("duration_sec", end.get("duration", 3))
    try:
        duration = float(raw_dur)
    except (TypeError, ValueError):
        duration = 3.0
    duration = max(1.0, min(5.0, duration))
    return {"text": text, "duration_sec": duration}


def normalize_storyboard(data: dict[str, Any]) -> dict[str, Any]:
    """Repair common Gemini shape mistakes in-place before schema validation."""
    music = data.get("music")
    if isinstance(music, dict) and "caption" not in music:
        parts = [
            str(music.get(k))
            for k in ("genre", "mood", "tempo", "style", "instruments", "description")
            if music.get(k)
        ]
        music["caption"] = ", ".join(parts) if parts else "gentle instrumental underscore, no vocals"
        music.setdefault("duration_sec", 75)
        music.setdefault("instrumental", True)
        data["music"] = music
    data["end_card"] = normalize_end_card(data.get("end_card"))
    data.setdefault("subtitle_language", "am")
    shots = data.get("shots") or []
    for i, shot in enumerate(shots, start=1):
        if not isinstance(shot, dict):
            continue
        shot.setdefault("id", f"shot_{i:02d}")
        shot.setdefault("duration_sec", 6)
        shot.setdefault("reason", shot.get("narration_en") or shot.get("narration") or "story beat")
        shot.setdefault("image_prompt", shot.get("prompt") or "Ethiopian highland countryside scene")
        shot.setdefault("motion_prompt", "slow gentle camera move, soft motion")
        shot.setdefault("narration", shot.get("narration_en") or shot.get("reason") or "A quiet memory.")
        shot.setdefault("narration_en", shot.get("narration") or "A quiet memory.")
        shot.setdefault("seed", 100 + i)
        shot.setdefault("shot_backend", None)
    data["shots"] = [s for s in shots if isinstance(s, dict)]
    return data


def load_storyboard(path: Path | None = None) -> dict[str, Any]:
    path = path or config.STORYBOARD_PATH
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    validate_storyboard(data)
    return data


def validate_storyboard(data: dict[str, Any]) -> None:
    # Always coerce Gemini title/subtitle end_card (and related) before schema check.
    normalize_storyboard(data)
    with config.SCHEMA_PATH.open(encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(instance=data, schema=schema)


def content_hash(*parts: Any) -> str:
    h = hashlib.sha256()
    for part in parts:
        if isinstance(part, (bytes, bytearray)):
            h.update(part)
        else:
            h.update(json.dumps(part, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    return h.hexdigest()[:16]


def cache_path(stage: str, key: str, suffix: str) -> Path:
    config.ensure_dirs()
    d = config.CACHE_DIR / stage
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{key}{suffix}"


def is_cached(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def log_run(
    *,
    stage: str,
    model: str,
    parameters: dict[str, Any] | None = None,
    seed: int | None = None,
    latency_ms: float | None = None,
    cost_usd: float | None = None,
    success: bool = True,
    error: str | None = None,
    output_path: str | None = None,
    job_id: str | None = None,
) -> None:
    config.ensure_dirs()
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "model": model,
        "parameters": parameters or {},
        "seed": seed,
        "latency_ms": round(latency_ms, 2) if latency_ms is not None else None,
        "cost_usd": cost_usd,
        "success": success,
        "error": error,
        "output_path": output_path,
        "job_id": job_id,
    }
    with config.RUNS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def timed(fn: Callable[[], T]) -> tuple[T, float]:
    start = time.perf_counter()
    result = fn()
    return result, (time.perf_counter() - start) * 1000


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def with_retries(fn: Callable[[], T]) -> T:
    return fn()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
