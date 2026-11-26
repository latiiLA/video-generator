"""Stage: draft or refine storyboard via Gemini."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from pipeline import config
from pipeline.common import (
    load_storyboard,
    log_run,
    normalize_storyboard,
    timed,
    validate_storyboard,
    write_json,
)


SYSTEM = """You are a film storyboard writer for short heritage films.
Return ONLY valid JSON matching the provided schema fields.
8-12 shots, each with reason, image_prompt, motion_prompt, narration (in the requested language),
and narration_en (English). Keep style_block and character consistent.
No text inside image prompts. Durations 5-8 seconds. Total film ~60-90s before end card.
music MUST be an object with string field "caption" and number "duration_sec" (30-120).
end_card MUST be an object with exactly:
  - "text": string (end-card line shown on screen)
  - "duration_sec": number between 1 and 5
Do NOT use title/subtitle fields on end_card.
"""


def _model_chain() -> list[str]:
    chain: list[str] = []
    for m in [config.GEMINI_MODEL, *config.GEMINI_MODEL_FALLBACKS]:
        if m and m not in chain:
            chain.append(m)
    return chain


def draft_from_storyline(storyline: str, language: str = "am") -> dict:
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY missing")

    from google import genai

    client = genai.Client(api_key=config.GEMINI_API_KEY)
    prompt = (
        f"Language for narration: {language}\n"
        f"Storyline:\n{storyline}\n\n"
        "Produce a complete storyboard JSON object with keys: "
        "title, logline, language, subtitle_language, audience, intent, style_block, "
        "character, tts, music, end_card, shots."
    )

    last_err: Exception | None = None
    for model in _model_chain():
        try:

            def call(m: str = model):
                return client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config={
                        "system_instruction": SYSTEM,
                        "response_mime_type": "application/json",
                    },
                )

            response, latency = timed(call)
            text = response.text or "{}"
            data = json.loads(text)
            data.setdefault("language", language)
            data.setdefault("subtitle_language", "en")
            data = normalize_storyboard(data)
            validate_storyboard(data)
            log_run(
                stage="script",
                model=model,
                parameters={"language": language, "storyline_len": len(storyline)},
                latency_ms=latency,
                cost_usd=0.0,
                success=True,
            )
            return data
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            msg = str(exc).lower()
            retryable = any(
                s in msg for s in ("503", "429", "unavailable", "high demand", "resource")
            )
            log_run(
                stage="script",
                model=model,
                success=False,
                error=str(exc),
                parameters={"retryable": retryable},
            )
            if not retryable:
                raise
            time.sleep(1.5)

    raise RuntimeError(f"All Gemini models failed for script: {last_err}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate or draft storyboard")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--from-storyline", type=str, default=None)
    parser.add_argument("--language", type=str, default="am")
    parser.add_argument("--storyboard", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=config.STORYBOARD_PATH)
    args = parser.parse_args(argv)

    config.ensure_dirs()
    sb_path = args.storyboard or args.out

    if args.from_storyline:
        data = draft_from_storyline(args.from_storyline, args.language)
        write_json(sb_path, data)
        print(f"Wrote storyboard to {sb_path}")
        return 0

    data = load_storyboard(sb_path)
    validate_storyboard(data)
    print(f"OK: storyboard valid ({len(data['shots'])} shots) @ {sb_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
