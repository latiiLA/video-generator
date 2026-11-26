"""Stage: Gemini TTS narration per shot."""

from __future__ import annotations

import argparse
import base64
import struct
import subprocess
import sys
import wave
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout
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


def _save_audio_bytes(out: Path, raw: bytes) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    if raw[:4] == b"RIFF":
        out.write_bytes(raw)
    else:
        _write_wav_pcm16(out, raw, 24000)


def _tts_chain() -> list[str]:
    # Prefer current Gemini 3.8 TTS models; older 2.5 preview paths are flaky.
    chain: list[str] = []
    for m in [
        config.GEMINI_TTS_MODEL,
        *config.GEMINI_TTS_FALLBACKS,
        "gemini-3.8-flash-tts",
        "gemini-3.8-flash-lite-tts",
    ]:
        if m and m not in chain:
            chain.append(m)
    return chain


def _run_with_timeout(fn, timeout_sec: float = 90.0):
    pool = ThreadPoolExecutor(max_workers=1)
    try:
        return pool.submit(fn).result(timeout=timeout_sec)
    finally:
        # Critical: wait=False or a hung HTTP call blocks forever on shutdown.
        pool.shutdown(wait=False, cancel_futures=True)


def _language_label(code: str) -> str:
    return {
        "am": "Amharic",
        "om": "Afaan Oromo",
        "en": "English",
    }.get((code or "en").lower().strip(), code or "English")


def _has_ethiopic(text: str) -> bool:
    return any("\u1200" <= ch <= "\u137F" for ch in text)


def _assert_usable_audio(path: Path, min_bytes: int = 8000) -> None:
    if not path.exists() or path.stat().st_size < min_bytes:
        size = path.stat().st_size if path.exists() else 0
        raise RuntimeError(f"TTS audio too small ({size} bytes): {path}")


def _tts_generate_content(
    text: str, style: str, voice: str, model: str, out: Path, language: str = "en"
) -> float:
    """Gemini TTS via generateContent (verbatim transcript + speech_metadata)."""
    from google import genai

    client = genai.Client(api_key=config.GEMINI_API_KEY)

    def call():
        return client.models.generate_content(
            model=model,
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": text,
                            "speech_metadata": {"style": style},
                        }
                    ],
                }
            ],
            config={
                "response_modalities": ["AUDIO"],
                "speech_config": {"voice_config": {"voice": voice}},
            },
        )

    response, latency = timed(lambda: _run_with_timeout(call, 90))
    try:
        data = response.candidates[0].content.parts[0].inline_data.data
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"No audio in generate_content response: {exc}") from exc
    if not data:
        raise RuntimeError("Empty audio in generate_content response")
    raw = base64.b64decode(data) if isinstance(data, str) else bytes(data)
    _save_audio_bytes(out, raw)
    _assert_usable_audio(out)
    return latency


def _tts_interactions(
    text: str, style: str, voice: str, model: str, out: Path, language: str = "en"
) -> float:
    """Gemini TTS via Interactions REST (SDK create() can hang indefinitely)."""
    import json

    import requests

    url = "https://generativelanguage.googleapis.com/v1beta/interactions"
    body = {
        "model": model,
        "input": [
            {
                "type": "user_input",
                "content": [
                    {
                        "type": "text",
                        # Verbatim transcript — do not wrap with English instructions
                        "text": text,
                        "annotations": [{"type": "speech_metadata", "style": style}],
                    }
                ],
            }
        ],
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": voice}]},
    }

    def call():
        r = requests.post(
            url,
            params={"key": config.GEMINI_API_KEY},
            headers={"Content-Type": "application/json"},
            data=json.dumps(body),
            timeout=90,
        )
        if not r.ok:
            raise RuntimeError(f"interactions HTTP {r.status_code}: {r.text[:500]}")
        return r.json()

    payload, latency = timed(call)
    audio_b64 = (payload.get("output_audio") or {}).get("data")
    if not audio_b64:
        for step in payload.get("steps") or []:
            for part in step.get("content") or []:
                if part.get("data"):
                    audio_b64 = part["data"]
                    break
            if audio_b64:
                break
    if not audio_b64:
        raise RuntimeError(f"No audio in TTS response keys={list(payload.keys())}")
    _save_audio_bytes(out, base64.b64decode(audio_b64))
    _assert_usable_audio(out)
    return latency


_EDGE_VOICES = {
    "am": "am-ET-MekdesNeural",
    "om": "am-ET-MekdesNeural",
    "en": "en-US-GuyNeural",  # adult male English narrator
}

# Map Gemini prebuilt voices → Edge when Gemini TTS is unavailable
_GEMINI_TO_EDGE_MALE = {
    "fenrir",
    "orus",
    "charon",
    "puck",
    "umbriel",
    "algenib",
    "enceladus",
    "iapetus",
    "alnilam",
    "gacrux",
    "pulcherrima",
    "achird",
    "zubenelgenubi",
    "vindemiatrix",
    "sadachbia",
    "sadaltager",
    "sulafat",
}


def _edge_voice_for(language: str, preferred: str | None = None) -> str:
    lang = (language or "en").lower()[:2]
    pref = (preferred or "").strip()
    if pref.endswith("Neural"):
        return pref
    if lang == "en":
        # Default English to male narrator; honor Gemini male voice names
        if not pref or pref.lower() in _GEMINI_TO_EDGE_MALE or pref.lower() == "fenrir":
            return "en-US-GuyNeural"
        if pref.lower() in {"kore", "aoede", "zephyr", "leda", "callirrhoe", "autonoe"}:
            return "en-US-JennyNeural"
        return "en-US-GuyNeural"
    return _EDGE_VOICES.get(lang, "en-US-GuyNeural")


def _tts_edge(
    text: str, out: Path, language: str = "en", preferred_voice: str | None = None
) -> float:
    """Microsoft Edge neural TTS — reliable when Gemini quota is exhausted."""
    import asyncio

    import edge_tts

    voice = _edge_voice_for(language, preferred_voice)

    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".edge.mp3")

    async def synthesize() -> None:
        communicate = edge_tts.Communicate(text, voice=voice, rate="-8%")
        await communicate.save(str(tmp))

    def call():
        asyncio.run(synthesize())
        ffmpeg = config.ffmpeg_exe()
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(tmp),
                "-ac",
                "1",
                "-ar",
                "24000",
                str(out),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        tmp.unlink(missing_ok=True)

    _, latency = timed(call)
    _assert_usable_audio(out)
    return latency


def _tts_windows_sapi(text: str, out: Path) -> float:
    """Last-resort English TTS so assembly can finish when Gemini hangs."""
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".sapi.wav")
    # Escape for PowerShell single-quoted string
    safe = text.replace("'", "''")
    ps = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$s.Rate = -2; $s.Volume = 100; "
        f"$s.SetOutputToWaveFile('{tmp.as_posix()}'); "
        f"$s.Speak('{safe}'); $s.Dispose()"
    )

    def call():
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            check=True,
            capture_output=True,
            text=True,
        )

    _, latency = timed(call)
    # Resample/normalize via ffmpeg to 24k mono for the rest of the pipeline
    ffmpeg = config.ffmpeg_exe()
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(tmp),
            "-ac",
            "1",
            "-ar",
            "24000",
            str(out),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    tmp.unlink(missing_ok=True)
    return latency


def synthesize_line(
    text: str, style: str, voice: str, out: Path, language: str = "en"
) -> dict:
    if not config.GEMINI_API_KEY:
        approx = max(2.0, len(text.split()) / 2.2)
        _silent_wav(out, approx)
        log_run(
            stage="narration",
            model="silent-placeholder",
            parameters={"reason": "no GEMINI_API_KEY", "voice": voice, "language": language},
            success=True,
            output_path=str(out),
        )
        return {"path": out, "placeholder": True}

    last_err: Exception | None = None
    edge_voice = _edge_voice_for(language, voice)

    # Edge first — reliable male English / Amharic when Gemini free TTS is rate-limited.
    try:
        latency = _tts_edge(text, out, language=language, preferred_voice=voice)
        log_run(
            stage="narration",
            model="edge-tts",
            parameters={
                "voice": edge_voice,
                "chars": len(text),
                "language": language,
            },
            latency_ms=latency,
            cost_usd=0.0,
            success=True,
            output_path=str(out),
        )
        return {"path": out, "placeholder": False, "fallback": False}
    except Exception as edge_exc:  # noqa: BLE001
        last_err = edge_exc
        log_run(
            stage="narration",
            model="edge-tts",
            success=False,
            error=str(edge_exc),
        )

    for model in _tts_chain():
        for method_name, method in (
            ("interactions", _tts_interactions),
            ("generate_content", _tts_generate_content),
        ):
            try:
                latency = method(text, style, voice, model, out, language)
                log_run(
                    stage="narration",
                    model=f"{model}/{method_name}",
                    parameters={
                        "voice": voice,
                        "style": style,
                        "chars": len(text),
                        "language": language,
                    },
                    latency_ms=latency,
                    cost_usd=0.0,
                    success=True,
                    output_path=str(out),
                )
                return {"path": out, "placeholder": False}
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                log_run(
                    stage="narration",
                    model=f"{model}/{method_name}",
                    success=False,
                    error=str(exc),
                )
                if "429" in str(exc) or "Rate limit" in str(exc):
                    break
        else:
            continue
        break

    if _has_ethiopic(text) or (language or "").lower().startswith(("am", "om")):
        raise RuntimeError(
            f"All TTS paths failed for Ethiopic/Amharic text: {last_err}"
        )

    try:
        latency = _tts_windows_sapi(text, out)
        _assert_usable_audio(out)
        log_run(
            stage="narration",
            model="windows-sapi-fallback",
            parameters={"voice": "system", "chars": len(text), "note": str(last_err)},
            latency_ms=latency,
            cost_usd=0.0,
            success=True,
            output_path=str(out),
        )
        return {"path": out, "placeholder": False, "fallback": True}
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"All TTS paths failed: {last_err}; sapi={exc}") from exc


def _spoken_text(shot: dict, language: str) -> str:
    """Prefer language-specific line; fall back to primary narration."""
    lang = (language or "en").lower().strip()
    if lang.startswith("am"):
        return (shot.get("narration_am") or shot.get("narration") or "").strip()
    if lang.startswith("om"):
        return (shot.get("narration_om") or shot.get("narration") or "").strip()
    return (shot.get("narration_en") or shot.get("narration") or "").strip()


def run(storyboard_path: Path | None = None, force: bool = False) -> list[Path]:
    config.ensure_dirs()
    sb = load_storyboard(storyboard_path)
    voice = (sb.get("tts") or {}).get("voice", "Kore")
    style = (sb.get("tts") or {}).get("style", "calm, warm, unhurried")
    language = (sb.get("language") or "am").strip()
    outs: list[Path] = []

    for shot in sb["shots"]:
        text = _spoken_text(shot, language)
        if not text:
            raise ValueError(f"{shot['id']} has no narration text for language={language}")
        key = content_hash(
            shot["id"],
            text,
            voice,
            style,
            language,
            config.TTS_BACKEND,
            config.GEMINI_TTS_MODEL,
        )
        cached = cache_path("narration", f"{shot['id']}_{key}", ".wav")
        final = config.OUTPUT_DIR / "narration" / f"{shot['id']}.wav"

        if not force and is_cached(cached):
            final.write_bytes(cached.read_bytes())
            outs.append(final)
            print(f"  {shot['id']}: cache hit")
            continue

        print(f"  {shot['id']}: synthesizing ({language})…", flush=True)
        synthesize_line(text, style, voice, cached, language=language)
        final.write_bytes(cached.read_bytes())
        outs.append(final)
        print(f"  {shot['id']}: ok ({final.stat().st_size} bytes)", flush=True)

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
