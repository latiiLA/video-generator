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


def load_storyboard(path: Path | None = None) -> dict[str, Any]:
    path = path or config.STORYBOARD_PATH
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    validate_storyboard(data)
    return data


def validate_storyboard(data: dict[str, Any]) -> None:
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
