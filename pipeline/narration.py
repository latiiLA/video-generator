"""Stage: Gemini TTS narration per shot."""

from __future__ import annotations

import argparse
import struct
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
    with_retries,
)


def _write_wav_pcm16(path: Path, pcm: bytes, sample_rate: int = 24000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)


def _silent_wav(path: Path, duration_sec: float, sample_rate: int = 24000) -> None:
    n = int(duration_sec * sample_rate)
    pcm = struct.pack(f"<{n}h", *([0] * n))
    _write_wav_pcm16(path, pcm, sample_rate)


def synthesize_line(text: str, style: str, voice: str, out: Path) -> dict:
    if not config.GEMINI_API_KEY:
        # Offline-friendly placeholder so assemble can be developed without keys
        approx = max(2.0, len(text.split()) / 2.2)
        _silent_wav(out, approx)
        log_run(
            stage="narration",
            model="silent-placeholder",
            parameters={"reason": "no GEMINI_API_KEY", "voice": voice},
            success=True,
            output_path=str(out),
        )
        return {"path": out, "placeholder": True}

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=config.GEMINI_API_KEY)

    def call():
        return client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=f"{style}. Speak clearly:\n{text}",
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
                    )
                ),
            ),
        )

    response, latency = timed(lambda: with_retries(call))
    inline = response.candidates[0].content.parts[0].inline_data
    data = inline.data
    # API may return raw PCM or WAV; write as WAV container if raw
    if data[:4] == b"RIFF":
        out.write_bytes(data)
    else:
        _write_wav_pcm16(out, data, 24000)

    log_run(
        stage="narration",
        model="gemini-2.5-flash-preview-tts",
        parameters={"voice": voice, "style": style, "chars": len(text)},
        latency_ms=latency,
        cost_usd=0.0,
        success=True,
        output_path=str(out),
    )
    return {"path": out, "placeholder": False}


def run(storyboard_path: Path | None = None, force: bool = False) -> list[Path]:
    config.ensure_dirs()
    sb = load_storyboard(storyboard_path)
    voice = (sb.get("tts") or {}).get("voice", "Kore")
    style = (sb.get("tts") or {}).get("style", "calm, warm, unhurried")
    outs: list[Path] = []

    for shot in sb["shots"]:
        key = content_hash(shot["id"], shot["narration"], voice, style, config.TTS_BACKEND)
        cached = cache_path("narration", f"{shot['id']}_{key}", ".wav")
        final = config.OUTPUT_DIR / "narration" / f"{shot['id']}.wav"

        if not force and is_cached(cached):
            final.write_bytes(cached.read_bytes())
            outs.append(final)
            continue

        synthesize_line(shot["narration"], style, voice, cached)
        final.write_bytes(cached.read_bytes())
        outs.append(final)

    print(f"Narration: {len(outs)} files in {config.OUTPUT_DIR / 'narration'}")
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
