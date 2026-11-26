"""Smoke-test providers and log latency to runs.jsonl."""

from __future__ import annotations

import shutil
import sys
import time

from pipeline import config
from pipeline.common import log_run, load_storyboard


def main() -> int:
    config.ensure_dirs()
    ok = True

    # Schema / storyboard
    t0 = time.perf_counter()
    try:
        sb = load_storyboard()
        log_run(
            stage="smoke",
            model="schema",
            latency_ms=(time.perf_counter() - t0) * 1000,
            success=True,
            parameters={"shots": len(sb["shots"])},
        )
        print("OK storyboard schema")
    except Exception as exc:  # noqa: BLE001
        ok = False
        log_run(stage="smoke", model="schema", success=False, error=str(exc))
        print("FAIL storyboard:", exc)

    # FFmpeg
    t0 = time.perf_counter()
    try:
        exe = config.ffmpeg_exe()
        log_run(
            stage="smoke",
            model="ffmpeg",
            latency_ms=(time.perf_counter() - t0) * 1000,
            success=True,
            parameters={"exe": exe},
        )
        print("OK ffmpeg:", exe)
    except Exception as exc:  # noqa: BLE001
        ok = False
        log_run(stage="smoke", model="ffmpeg", success=False, error=str(exc))
        print("FAIL ffmpeg:", exc)

    # Gemini
    t0 = time.perf_counter()
    if config.GEMINI_API_KEY:
        try:
            from google import genai

            client = genai.Client(api_key=config.GEMINI_API_KEY)
            client.models.generate_content(
                model=config.GEMINI_MODEL, contents="Reply with OK"
            )
            log_run(
                stage="smoke",
                model=config.GEMINI_MODEL,
                latency_ms=(time.perf_counter() - t0) * 1000,
                cost_usd=0.0,
                success=True,
            )
            print("OK gemini:", config.GEMINI_MODEL)
        except Exception as exc:  # noqa: BLE001
            ok = False
            log_run(stage="smoke", model="gemini", success=False, error=str(exc))
            print("FAIL gemini:", exc)
    else:
        print("SKIP gemini (no GEMINI_API_KEY)")
        log_run(stage="smoke", model="gemini", success=True, parameters={"skipped": True})

    # Cloudflare
    t0 = time.perf_counter()
    if config.CLOUDFLARE_ACCOUNT_ID and config.CLOUDFLARE_API_TOKEN:
        try:
            import requests

            url = (
                f"https://api.cloudflare.com/client/v4/accounts/"
                f"{config.CLOUDFLARE_ACCOUNT_ID}/ai/run/{config.IMAGE_MODEL}"
            )
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {config.CLOUDFLARE_API_TOKEN}"},
                json={"prompt": "a simple warm clay pot on a wooden table, no text"},
                timeout=120,
            )
            r.raise_for_status()
            log_run(
                stage="smoke",
                model=config.IMAGE_MODEL,
                latency_ms=(time.perf_counter() - t0) * 1000,
                cost_usd=0.0,
                success=True,
            )
            print("OK cloudflare flux")
        except Exception as exc:  # noqa: BLE001
            ok = False
            log_run(stage="smoke", model="cloudflare", success=False, error=str(exc))
            print("FAIL cloudflare:", exc)
    else:
        print("SKIP cloudflare (missing credentials)")
        log_run(stage="smoke", model="cloudflare", success=True, parameters={"skipped": True})

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
