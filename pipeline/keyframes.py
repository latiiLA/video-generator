"""Stage: generate keyframe stills (FLUX via Cloudflare, with local placeholder)."""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

from pipeline import config
from pipeline.common import (
    cache_path,
    content_hash,
    is_cached,
    load_storyboard,
    log_run,
    timed,
    with_retries,
)


def _placeholder_image(prompt: str, shot_id: str, out: Path, size=(768, 1344)) -> None:
    img = Image.new("RGB", size, (42, 28, 18))
    draw = ImageDraw.Draw(img)
    # warm gradient-ish blocks
    for i in range(0, size[1], 8):
        tone = 42 + (i * 40) // size[1]
        draw.rectangle([0, i, size[0], i + 8], fill=(tone, tone // 2, 20))
    text = f"{shot_id}\n{prompt[:120]}"
    draw.multiline_text((40, 80), text, fill=(240, 220, 180), spacing=6)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG")


def generate_flux(prompt: str, seed: int | None, out: Path) -> dict:
    if not (config.CLOUDFLARE_ACCOUNT_ID and config.CLOUDFLARE_API_TOKEN):
        _placeholder_image(prompt, out.stem, out)
        log_run(
            stage="keyframes",
            model="placeholder-pillow",
            parameters={"reason": "missing Cloudflare credentials"},
            seed=seed,
            success=True,
            output_path=str(out),
        )
        return {"path": out, "placeholder": True}

    url = (
        f"https://api.cloudflare.com/client/v4/accounts/"
        f"{config.CLOUDFLARE_ACCOUNT_ID}/ai/run/{config.IMAGE_MODEL}"
    )
    headers = {"Authorization": f"Bearer {config.CLOUDFLARE_API_TOKEN}"}
    body = {"prompt": prompt}
    if seed is not None:
        body["seed"] = seed

    def call():
        r = requests.post(url, headers=headers, json=body, timeout=120)
        r.raise_for_status()
        return r.content

    raw, latency = timed(lambda: with_retries(call))
    # Workers AI may return raw image bytes or JSON with base64; handle raw image
    try:
        Image.open(io.BytesIO(raw)).verify()
        out.write_bytes(raw)
    except Exception:
        # JSON envelope
        import base64
        import json

        payload = json.loads(raw.decode("utf-8"))
        b64 = payload.get("result", {}).get("image") or payload.get("image")
        if not b64:
            raise RuntimeError(f"Unexpected Cloudflare response: {payload}")
        out.write_bytes(base64.b64decode(b64))

    log_run(
        stage="keyframes",
        model=config.IMAGE_MODEL,
        parameters={"prompt_len": len(prompt)},
        seed=seed,
        latency_ms=latency,
        cost_usd=0.0,
        success=True,
        output_path=str(out),
    )
    return {"path": out, "placeholder": False}


def full_prompt(sb: dict, shot: dict) -> str:
    return (
        f"{shot['image_prompt']}. Character: {sb['character']['description']}. "
        f"Style: {sb['style_block']}."
    )


def run_reference(sb: dict, force: bool = False) -> Path:
    config.ensure_dirs()
    prompt = (
        f"Character reference sheet, front view, neutral pose. "
        f"{sb['character']['description']}. Style: {sb['style_block']}."
    )
    key = content_hash("ref", prompt, config.IMAGE_BACKEND)
    cached = cache_path("references", key, ".png")
    final = config.OUTPUT_DIR / "references" / "character.png"
    if force or not is_cached(cached):
        generate_flux(prompt, 42, cached)
    final.write_bytes(cached.read_bytes())
    return final


def run(storyboard_path: Path | None = None, force: bool = False) -> list[Path]:
    config.ensure_dirs()
    sb = load_storyboard(storyboard_path)
    run_reference(sb, force=force)
    outs: list[Path] = []

    for shot in sb["shots"]:
        prompt = full_prompt(sb, shot)
        key = content_hash(shot["id"], prompt, shot.get("seed"), config.IMAGE_BACKEND)
        cached = cache_path("keyframes", f"{shot['id']}_{key}", ".png")
        final = config.OUTPUT_DIR / "keyframes" / f"{shot['id']}.png"

        if not force and is_cached(cached):
            final.write_bytes(cached.read_bytes())
            outs.append(final)
            continue

        generate_flux(prompt, shot.get("seed"), cached)
        final.write_bytes(cached.read_bytes())
        outs.append(final)

    print(f"Keyframes: {len(outs)} images")
    return outs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--storyboard", type=Path, default=None)
    args = parser.parse_args(argv)
    run(args.storyboard, force=args.force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
