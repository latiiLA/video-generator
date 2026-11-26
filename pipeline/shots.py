"""Stage: moving shots — Wan / Hunyuan hooks + Ken Burns fallback."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from pipeline import config
from pipeline.common import (
    cache_path,
    content_hash,
    is_cached,
    load_storyboard,
    log_run,
    timed,
)


def ken_burns(image: Path, duration: float, out: Path, seed: int | None = None) -> None:
    """Slow pan/zoom over a still. Works without GPU."""
    frames = max(int(duration * 24), 24)
    zoom_in = True if seed is None else (seed % 2 == 0)
    if zoom_in:
        z = (
            f"zoompan=z='min(zoom+0.0008,1.12)'"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=720x1280:fps=24"
        )
    else:
        z = (
            f"zoompan=z='if(eq(on,1),1.12,max(zoom-0.0008,1.0))'"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=720x1280:fps=24"
        )

    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        config.ffmpeg_exe(),
        "-y",
        "-loop",
        "1",
        "-i",
        str(image),
        "-vf",
        z,
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-an",
        str(out),
    ]

    def call():
        subprocess.run(cmd, check=True, capture_output=True)

    _, latency = timed(call)
    log_run(
        stage="shots",
        model="ffmpeg-kenburns",
        parameters={"duration": duration, "zoom_in": zoom_in},
        seed=seed,
        latency_ms=latency,
        cost_usd=0.0,
        success=True,
        output_path=str(out),
    )


def try_wan_or_hunyuan(backend: str, image: Path, motion: str, duration: float, out: Path) -> bool:
    """Pick up GPU clips exported from Kaggle/Colab; otherwise signal fallback."""
    marker = config.OUTPUT_DIR / "shots" / "external" / f"{out.stem}_{backend}.mp4"
    if marker.exists() and marker.stat().st_size > 0:
        shutil.copy(marker, out)
        log_run(
            stage="shots",
            model=backend,
            parameters={"source": str(marker), "motion": motion, "duration": duration},
            success=True,
            output_path=str(out),
        )
        return True

    log_run(
        stage="shots",
        model=backend,
        parameters={"motion": motion, "image": str(image)},
        success=False,
        error="GPU clip not present; use notebooks/ then re-run, or fall back to kenburns",
    )
    return False


def resolve_backend(shot: dict) -> list[str]:
    preferred = (shot.get("shot_backend") or config.SHOT_BACKEND or "kenburns").lower()
    chain = [preferred]
    for b in config.SHOT_FALLBACKS:
        if b not in chain:
            chain.append(b)
    if "kenburns" not in chain:
        chain.append("kenburns")
    return chain


def run(storyboard_path: Path | None = None, force: bool = False) -> list[Path]:
    config.ensure_dirs()
    sb = load_storyboard(storyboard_path)
    outs: list[Path] = []

    for shot in sb["shots"]:
        image = config.OUTPUT_DIR / "keyframes" / f"{shot['id']}.png"
        if not image.exists():
            raise FileNotFoundError(f"Missing keyframe {image}; run keyframes stage first")

        key = content_hash(
            shot["id"],
            shot["motion_prompt"],
            shot["duration_sec"],
            shot.get("seed"),
            config.SHOT_BACKEND,
            image.read_bytes()[:4096],
        )
        cached = cache_path("shots", f"{shot['id']}_{key}", ".mp4")
        final = config.OUTPUT_DIR / "shots" / f"{shot['id']}.mp4"

        if not force and is_cached(cached):
            final.write_bytes(cached.read_bytes())
            outs.append(final)
            continue

        made = False
        last_err = None
        for backend in resolve_backend(shot):
            try:
                if backend in ("wan", "hunyuan"):
                    made = try_wan_or_hunyuan(
                        backend, image, shot["motion_prompt"], shot["duration_sec"], cached
                    )
                elif backend == "kenburns":
                    ken_burns(image, float(shot["duration_sec"]), cached, shot.get("seed"))
                    made = True
                if made:
                    break
            except Exception as exc:  # noqa: BLE001
                last_err = str(exc)
                log_run(
                    stage="shots",
                    model=backend,
                    success=False,
                    error=last_err,
                    parameters={"shot": shot["id"]},
                )

        if not made:
            raise RuntimeError(f"All shot backends failed for {shot['id']}: {last_err}")

        final.write_bytes(cached.read_bytes())
        outs.append(final)

    print(f"Shots: {len(outs)} clips")
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
