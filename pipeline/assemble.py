"""Stage: FFmpeg assembly — duck, subtitles, loudnorm, end card, dual aspect."""

from __future__ import annotations

import argparse
import subprocess
import sys
import wave
from pathlib import Path

from pipeline import config
from pipeline.common import load_storyboard, log_run, timed


def _ffmpeg(*args: str) -> None:
    cmd = [config.ffmpeg_exe(), "-y", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[-2000:])


def _wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


def write_srt(sb: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    t = 0.0
    for i, shot in enumerate(sb["shots"], start=1):
        narr = config.OUTPUT_DIR / "narration" / f"{shot['id']}.wav"
        dur = _wav_duration(narr) if narr.exists() else float(shot["duration_sec"])
        start = t
        end = t + dur
        lines.append(str(i))
        lines.append(f"{_ts(start)} --> {_ts(end)}")
        lines.append(shot["narration_en"])
        lines.append("")
        t = end
    path.write_text("\n".join(lines), encoding="utf-8")


def _ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def concat_narration(sb: dict, out: Path) -> float:
    list_file = config.OUTPUT_DIR / "narration" / "concat.txt"
    paths = []
    for shot in sb["shots"]:
        p = config.OUTPUT_DIR / "narration" / f"{shot['id']}.wav"
        if not p.exists():
            raise FileNotFoundError(p)
        paths.append(p)
    list_file.write_text(
        "".join(f"file '{p.resolve().as_posix()}'\n" for p in paths),
        encoding="utf-8",
    )
    _ffmpeg("-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(out))
    return _wav_duration(out)


def make_end_card(text: str, duration: float, out: Path, size: str = "720x1280") -> None:
    safe = text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    _ffmpeg(
        "-f",
        "lavfi",
        "-i",
        f"color=c=0x1a120c:s={size}:d={duration}",
        "-vf",
        f"drawtext=text='{safe}':fontcolor=0xf5e6c8:fontsize=36:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(out),
    )


def build_picture_timeline(sb: dict, vertical: Path) -> None:
    parts_dir = config.OUTPUT_DIR / "film" / "parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    part_paths = []
    for shot in sb["shots"]:
        src = config.OUTPUT_DIR / "shots" / f"{shot['id']}.mp4"
        narr = config.OUTPUT_DIR / "narration" / f"{shot['id']}.wav"
        dur = _wav_duration(narr)
        part = parts_dir / f"{shot['id']}.mp4"
        _ffmpeg(
            "-i",
            str(src),
            "-vf",
            "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=24",
            "-t",
            str(dur),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(part),
        )
        part_paths.append(part)

    end = parts_dir / "endcard.mp4"
    make_end_card(sb["end_card"]["text"], float(sb["end_card"]["duration_sec"]), end)
    part_paths.append(end)

    concat_list = parts_dir / "concat.txt"
    concat_list.write_text(
        "".join(f"file '{p.resolve().as_posix()}'\n" for p in part_paths),
        encoding="utf-8",
    )
    _ffmpeg("-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(vertical))


def mix_audio(narr: Path, music: Path, out: Path) -> None:
    # Normalize both to 48k mono first so silent/odd WAV rates don't wreck the mix
    _ffmpeg(
        "-i",
        str(narr),
        "-stream_loop",
        "-1",
        "-i",
        str(music),
        "-filter_complex",
        "[0:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=mono,volume=2.0[voice];"
        "[1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=mono,volume=0.25[musicbed];"
        "[musicbed][voice]sidechaincompress=threshold=0.02:ratio=6:attack=300:release=1500[ducked];"
        "[voice][ducked]amix=inputs=2:duration=first:dropout_transition=2[mix];"
        "[mix]loudnorm=I=-14:TP=-1.5:LRA=11[aout]",
        "-map",
        "[aout]",
        "-ar",
        "48000",
        "-ac",
        "1",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        str(out),
    )


def burn_subs_and_mux(video: Path, audio: Path, srt: Path, out: Path) -> None:
    srt_esc = srt.resolve().as_posix().replace(":", "\\:")
    _ffmpeg(
        "-i",
        str(video),
        "-i",
        str(audio),
        "-vf",
        f"subtitles='{srt_esc}':force_style='FontSize=22,PrimaryColour=&H00E6F5&,Outline=1'",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-shortest",
        "-pix_fmt",
        "yuv420p",
        str(out),
    )


def to_horizontal(vertical: Path, out: Path) -> None:
    _ffmpeg(
        "-i",
        str(vertical),
        "-vf",
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x1a120c",
        "-c:a",
        "copy",
        str(out),
    )


def run_radio(storyboard_path: Path | None = None) -> Path:
    config.ffmpeg_exe()  # raise early if missing
    config.ensure_dirs()
    sb = load_storyboard(storyboard_path)
    narr = config.OUTPUT_DIR / "film" / "narration_full.wav"
    duration = concat_narration(sb, narr)
    music = config.OUTPUT_DIR / "music" / "score.wav"
    if not music.exists():
        from pipeline import music as music_stage

        music_stage.run(storyboard_path)

    mixed = config.OUTPUT_DIR / "film" / "radio_audio.aac"
    mix_audio(narr, music, mixed)
    out = config.OUTPUT_DIR / "film" / "radio_cut.mp4"
    total = duration + float(sb["end_card"]["duration_sec"])
    _ffmpeg(
        "-f",
        "lavfi",
        "-i",
        f"color=c=black:s=720x1280:d={total}",
        "-i",
        str(mixed),
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-shortest",
        "-pix_fmt",
        "yuv420p",
        str(out),
    )
    log_run(stage="assemble", model="ffmpeg-radio", success=True, output_path=str(out))
    print(f"Radio cut: {out}")
    return out


def run(storyboard_path: Path | None = None) -> dict[str, Path]:
    config.ffmpeg_exe()
    config.ensure_dirs()
    sb = load_storyboard(storyboard_path)

    narr = config.OUTPUT_DIR / "film" / "narration_full.wav"
    concat_narration(sb, narr)
    music = config.OUTPUT_DIR / "music" / "score.wav"
    if not music.exists():
        raise FileNotFoundError("Run music stage first")

    srt = config.OUTPUT_DIR / "subs" / "en.srt"
    write_srt(sb, srt)

    picture = config.OUTPUT_DIR / "film" / "picture_vertical.mp4"
    build_picture_timeline(sb, picture)

    mixed = config.OUTPUT_DIR / "film" / "mix.aac"
    mix_audio(narr, music, mixed)

    vertical = config.OUTPUT_DIR / "film" / "final_9x16.mp4"
    horizontal = config.OUTPUT_DIR / "film" / "final_16x9.mp4"

    def build():
        burn_subs_and_mux(picture, mixed, srt, vertical)
        to_horizontal(vertical, horizontal)

    _, latency = timed(build)
    log_run(
        stage="assemble",
        model="ffmpeg",
        parameters={"outputs": ["final_9x16.mp4", "final_16x9.mp4"]},
        latency_ms=latency,
        cost_usd=0.0,
        success=True,
        output_path=str(vertical),
    )
    print(f"Film: {vertical}\n       {horizontal}")
    return {"vertical": vertical, "horizontal": horizontal}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--radio", action="store_true")
    parser.add_argument("--storyboard", type=Path, default=None)
    args = parser.parse_args(argv)
    if args.radio:
        run_radio(args.storyboard)
    else:
        run(args.storyboard)
    return 0


if __name__ == "__main__":
    sys.exit(main())
