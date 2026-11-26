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


def _cue_text(shot: dict, field: str) -> str:
    text = (shot.get(field) or "").strip()
    if text:
        return text
    # Prefer the spoken `narration` line (often the primary language) before English.
    return (shot.get("narration") or shot.get("narration_en") or "").strip()


def write_srt(sb: dict, path: Path, field: str = "narration_en") -> None:
    """Write a single-language SRT timed to narration WAVs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    t = 0.0
    for i, shot in enumerate(sb["shots"], start=1):
        narr = config.OUTPUT_DIR / "narration" / f"{shot['id']}.wav"
        dur = _wav_duration(narr) if narr.exists() else float(shot["duration_sec"])
        start = t
        end = t + dur
        lines.append(str(i))
        lines.append(f"{_ts(start)} --> {_ts(end)}")
        lines.append(_cue_text(shot, field))
        lines.append("")
        t = end
    # UTF-8 BOM helps libass pick up Ethiopic / Latin mixed scripts on Windows
    path.write_text("\n".join(lines), encoding="utf-8-sig")


def _subtitle_lang(sb: dict) -> str:
    raw = (sb.get("subtitle_language") or sb.get("language") or "am").strip().lower()
    # Prefer Amharic when mixed legacy values appear
    if raw in {"am", "amharic"} or raw.startswith("am"):
        return "am"
    if "am" in raw.split("+") and "en" not in raw and "om" not in raw:
        return "am"
    if raw in {"en", "english"} or raw.startswith("en"):
        return "en"
    if raw in {"om", "oromo", "om+en", "en+om"} or "om" in raw:
        return "om"
    return "am"


def _subtitle_field(sb: dict) -> str:
    return {
        "am": "narration_am",
        "om": "narration_om",
        "en": "narration_en",
    }.get(_subtitle_lang(sb), "narration_am")


def _subtitle_font_style(single_language: bool = True) -> str:
    """Prefer a Windows font that covers Ethiopic + Latin."""
    fonts = [
        Path(r"C:\Windows\Fonts\ebrima.ttf"),
        Path(r"C:\Windows\Fonts\nyala.ttf"),
        Path(r"C:\Windows\Fonts\seguisym.ttf"),
    ]
    # Single-language Amharic can use a larger readable size
    size = 22 if single_language else 15
    margin = 48 if single_language else 36
    for font in fonts:
        if font.exists():
            return (
                f"FontName={font.stem},FontSize={size},PrimaryColour=&H00E6F5&,"
                f"Outline=1,Shadow=0,MarginV={margin},BorderStyle=1"
            )
    return f"FontSize={size},PrimaryColour=&H00E6F5&,Outline=1,MarginV={margin}"


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


ASPECT_SPECS = {
    "9x16": {"size": "720x1280", "w": 720, "h": 1280, "shots_subdir": None},
    "16x9": {"size": "1920x1080", "w": 1920, "h": 1080, "shots_subdir": "16x9"},
}


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


def _shot_source(shot_id: str, aspect: str) -> Path:
    spec = ASPECT_SPECS[aspect]
    root = config.OUTPUT_DIR / "shots"
    if spec["shots_subdir"]:
        candidate = root / spec["shots_subdir"] / f"{shot_id}.mp4"
        if candidate.exists():
            return candidate
    return root / f"{shot_id}.mp4"


def build_picture_timeline(sb: dict, out: Path, aspect: str = "9x16") -> None:
    """Assemble a full picture track for one aspect.

    16:9 uses true landscape shot clips (1920x1080), not a letterboxed 9:16 master.
    """
    spec = ASPECT_SPECS[aspect]
    w, h = spec["w"], spec["h"]
    parts_dir = config.OUTPUT_DIR / "film" / f"parts_{aspect}"
    parts_dir.mkdir(parents=True, exist_ok=True)
    part_paths = []
    for shot in sb["shots"]:
        src = _shot_source(shot["id"], aspect)
        if not src.exists():
            raise FileNotFoundError(f"Missing shot clip for {aspect}: {src}")
        narr = config.OUTPUT_DIR / "narration" / f"{shot['id']}.wav"
        dur = _wav_duration(narr)
        part = parts_dir / f"{shot['id']}.mp4"
        _ffmpeg(
            "-i",
            str(src),
            "-vf",
            f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps=24",
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
    make_end_card(
        sb["end_card"]["text"],
        float(sb["end_card"]["duration_sec"]),
        end,
        size=spec["size"],
    )
    part_paths.append(end)

    concat_list = parts_dir / "concat.txt"
    concat_list.write_text(
        "".join(f"file '{p.resolve().as_posix()}'\n" for p in part_paths),
        encoding="utf-8",
    )
    _ffmpeg("-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(out))


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
    fonts_dir = Path(r"C:\Windows\Fonts")
    style = _subtitle_font_style(single_language=True)
    if fonts_dir.is_dir():
        fonts_esc = fonts_dir.as_posix().replace(":", "\\:")
        vf = f"subtitles='{srt_esc}':fontsdir='{fonts_esc}':force_style='{style}'"
    else:
        vf = f"subtitles='{srt_esc}':force_style='{style}'"
    _ffmpeg(
        "-i",
        str(video),
        "-i",
        str(audio),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-shortest",
        "-pix_fmt",
        "yuv420p",
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

    subs_dir = config.OUTPUT_DIR / "subs"
    field = _subtitle_field(sb)
    lang = _subtitle_lang(sb)
    srt = subs_dir / f"{lang}.srt"
    write_srt(sb, srt, field=field)
    # Keep a convenient alias for Amharic-primary builds
    if lang == "am" and srt.name != "am.srt":
        write_srt(sb, subs_dir / "am.srt", field="narration_am")

    picture_v = config.OUTPUT_DIR / "film" / "picture_9x16.mp4"
    picture_h = config.OUTPUT_DIR / "film" / "picture_16x9.mp4"

    mixed = config.OUTPUT_DIR / "film" / "mix.aac"
    mix_audio(narr, music, mixed)

    vertical = config.OUTPUT_DIR / "film" / "final_9x16.mp4"
    horizontal = config.OUTPUT_DIR / "film" / "final_16x9.mp4"

    def build():
        build_picture_timeline(sb, picture_v, aspect="9x16")
        build_picture_timeline(sb, picture_h, aspect="16x9")
        burn_subs_and_mux(picture_v, mixed, srt, vertical)
        burn_subs_and_mux(picture_h, mixed, srt, horizontal)

    _, latency = timed(build)
    log_run(
        stage="assemble",
        model="ffmpeg",
        parameters={
            "outputs": ["final_9x16.mp4", "final_16x9.mp4"],
            "subtitles": [srt.name],
            "subtitle_language": lang,
            "aspect_mode": "native-dual",
        },
        latency_ms=latency,
        cost_usd=0.0,
        success=True,
        output_path=str(vertical),
    )
    print(f"Film: {vertical}\n       {horizontal}")
    print(f"Subs ({lang} only): {srt}")
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
