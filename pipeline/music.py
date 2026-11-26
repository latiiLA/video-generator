"""Stage: score generation (ACE-Step via notebook export) + procedural bed fallback."""

from __future__ import annotations

import argparse
import math
import shutil
import struct
import subprocess
import sys
import wave
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


def _write_soft_bed(path: Path, duration_sec: float, bpm: int = 72, sr: int = 44100) -> None:
    """Simple soft sine bed so assembly works without GPU music."""
    n = int(duration_sec * sr)
    freq = 110.0
    frames = []
    for i in range(n):
        t = i / sr
        env = 0.15 + 0.05 * math.sin(2 * math.pi * (bpm / 60.0) * t)
        sample = env * (
            0.4 * math.sin(2 * math.pi * freq * t)
            + 0.25 * math.sin(2 * math.pi * freq * 1.5 * t)
            + 0.15 * math.sin(2 * math.pi * freq * 2 * t)
        )
        frames.append(int(max(-1.0, min(1.0, sample)) * 32767))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(struct.pack(f"<{n}h", *frames))


def try_acestep_export(sb: dict, out: Path) -> bool:
    cand_dir = config.OUTPUT_DIR / "music" / "candidates"
    if not cand_dir.exists():
        return False
    files = sorted(cand_dir.glob("*.wav")) + sorted(cand_dir.glob("*.mp3"))
    if not files:
        return False
    chosen = files[0]
    target = out
    if chosen.suffix.lower() == ".mp3":
        target = out.with_suffix(".wav")
        subprocess.run(
            [config.ffmpeg_exe(), "-y", "-i", str(chosen), str(target)],
            check=True,
            capture_output=True,
        )
    else:
        shutil.copy(chosen, target)
    log_run(
        stage="music",
        model="ace-step-1.5",
        parameters={"caption": sb["music"]["caption"], "chosen": chosen.name},
        success=True,
        output_path=str(target),
    )
    return True


def run(storyboard_path: Path | None = None, force: bool = False) -> Path:
    config.ensure_dirs()
    sb = load_storyboard(storyboard_path)
    music = sb["music"]
    key = content_hash(music, config.MUSIC_BACKEND)
    cached = cache_path("music", key, ".wav")
    final = config.OUTPUT_DIR / "music" / "score.wav"

    if not force and is_cached(cached):
        final.write_bytes(cached.read_bytes())
        return final

    if try_acestep_export(sb, cached):
        final.write_bytes(cached.read_bytes())
        return final

    def call():
        _write_soft_bed(
            cached,
            float(music.get("duration_sec", 75)),
            int(music.get("tempo_bpm", 72)),
        )

    _, latency = timed(call)
    log_run(
        stage="music",
        model="procedural-bed",
        parameters={
            "reason": "no ACE-Step candidate in outputs/music/candidates",
            "caption": music["caption"],
        },
        latency_ms=latency,
        cost_usd=0.0,
        success=True,
        output_path=str(cached),
    )
    final.write_bytes(cached.read_bytes())
    print(f"Music: {final} (procedural bed; drop ACE-Step wav into outputs/music/candidates)")
    return final


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--storyboard", type=Path, default=None)
    args = parser.parse_args(argv)
    run(args.storyboard, force=args.force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
