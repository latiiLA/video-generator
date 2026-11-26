"""Stage: draft or refine storyboard via Gemini."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pipeline import config
from pipeline.common import load_storyboard, log_run, timed, validate_storyboard, write_json


SYSTEM = """You are a film storyboard writer for short heritage films.
Return ONLY valid JSON matching the provided schema fields.
8-12 shots, each with reason, image_prompt, motion_prompt, narration (in the requested language),
and narration_en (English). Keep style_block and character consistent.
No text inside image prompts. Durations 5-8 seconds. Total film ~60-90s before end card.
"""


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

    def call():
        return client.models.generate_content(
            model="gemini-2.0-flash",
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
    validate_storyboard(data)
    log_run(
        stage="script",
        model="gemini-2.0-flash",
        parameters={"language": language, "storyline_len": len(storyline)},
        latency_ms=latency,
        cost_usd=0.0,
        success=True,
    )
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate or draft storyboard")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--from-storyline", type=str, default=None)
    parser.add_argument("--language", type=str, default="am")
    parser.add_argument("--out", type=Path, default=config.STORYBOARD_PATH)
    args = parser.parse_args(argv)

    config.ensure_dirs()

    if args.from_storyline:
        data = draft_from_storyline(args.from_storyline, args.language)
        write_json(args.out, data)
        print(f"Wrote storyboard to {args.out}")
        return 0

    data = load_storyboard(args.out if args.out.exists() else None)
    validate_storyboard(data)
    print(f"OK: storyboard valid ({len(data['shots'])} shots)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
