"""Stage: Gemini TTS narration per shot (Interactions API)."""

from __future__ import annotations

import argparse
import base64
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


def _tts_chain() -> list[str]:
    chain: list[str] = []
    for m in [config.GEMINI_TTS_MODEL, *config.GEMINI_TTS_FALLBACKS]:
        if m and m not in chain:
            chain.append(m)
    return chain


def synthesize_line(text: str, style: str, voice: str, out: Path) -> dict:
    if not config.GEMINI_API_KEY:
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

    client = genai.Client(
        api_key=config.GEMINI_API_KEY,
        http_options={"api_version": "v1beta"},
    )

    last_err: Exception | None = None
    for model in _tts_chain():
        try:

            def call(m: str = model):
                return client.interactions.create(
                    model=m,
                    input=[
                        {
                            "type": "user_input",
                            "content": [
                                {
                                    "type": "text",
                                    "text": text,
                                    "annotations": [
                                        {
                                            "type": "speech_metadata",
                                            "style": style,
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                    response_format={"type": "audio"},
                    generation_config={
                        "speech_config": [
                            {"voice": voice},
                        ]
                    },
                )

            interaction, latency = timed(call)
            audio_b64 = None
            if getattr(interaction, "output_audio", None) is not None:
                audio_b64 = getattr(interaction.output_audio, "data", None)
            if not audio_b64:
                # Fallback: walk steps for audio content
                for step in getattr(interaction, "steps", []) or []:
                    for part in getattr(step, "content", []) or []:
                        data = getattr(part, "data", None)
                        if data:
                            audio_b64 = data
                            break
            if not audio_b64:
                raise RuntimeError(f"No audio in TTS response: {interaction}")

            raw = base64.b64decode(audio_b64)
            out.parent.mkdir(parents=True, exist_ok=True)
            if raw[:4] == b"RIFF":
                out.write_bytes(raw)
            else:
                _write_wav_pcm16(out, raw, 24000)

            log_run(
                stage="narration",
                model=model,
                parameters={"voice": voice, "style": style, "chars": len(text)},
                latency_ms=latency,
                cost_usd=0.0,
                success=True,
                output_path=str(out),
            )
            return {"path": out, "placeholder": False}
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            log_run(stage="narration", model=model, success=False, error=str(exc))
            msg = str(exc).lower()
            if not any(
                s in msg
                for s in ("503", "429", "unavailable", "high demand", "400", "invalid")
            ):
                raise

    raise RuntimeError(f"All Gemini TTS models failed: {last_err}")


def run(storyboard_path: Path | None = None, force: bool = False) -> list[Path]:
    config.ensure_dirs()
    sb = load_storyboard(storyboard_path)
    voice = (sb.get("tts") or {}).get("voice", "Kore")
    style = (sb.get("tts") or {}).get("style", "calm, warm, unhurried")
    outs: list[Path] = []

    for shot in sb["shots"]:
        key = content_hash(
            shot["id"], shot["narration"], voice, style, config.TTS_BACKEND, config.GEMINI_TTS_MODEL
        )
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
