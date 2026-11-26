"""Smoke-test Amharic TTS paths."""
from __future__ import annotations

import base64
import time
from pathlib import Path

from google import genai
from google.genai import types

from pipeline import config

OUT = Path("outputs/debug")
OUT.mkdir(parents=True, exist_ok=True)
TEXT = "በሰባተኛ ክፍል ነበርኩ ለመጀመሪያ ጊዜ የአያቴን የገጠር ቤት ስጎበኝ።"
STYLE = "warm, nostalgic, unhurried"


def save_audio(path: Path, data) -> int:
    raw = base64.b64decode(data) if isinstance(data, str) else bytes(data)
    if raw[:4] != b"RIFF":
        import wave

        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(raw)
    else:
        path.write_bytes(raw)
    return len(raw)


def try_interactions(model: str) -> None:
    print(f"interactions {model} …", flush=True)
    client = genai.Client(
        api_key=config.GEMINI_API_KEY,
        http_options={"api_version": "v1beta"},
    )
    t0 = time.time()
    inter = client.interactions.create(
        model=model,
        input=[
            {
                "type": "user_input",
                "content": [
                    {
                        "type": "text",
                        "text": TEXT,
                        "annotations": [{"type": "speech_metadata", "style": STYLE}],
                    }
                ],
            }
        ],
        response_format={"type": "audio"},
        generation_config={"speech_config": [{"voice": "Kore"}]},
    )
    audio = getattr(getattr(inter, "output_audio", None), "data", None)
    if not audio:
        raise RuntimeError(f"no audio: {inter}")
    n = save_audio(OUT / f"am_inter_{model}.wav", audio)
    print(f"OK interactions {model} bytes={n} sec={time.time()-t0:.1f}", flush=True)


def try_generate(model: str) -> None:
    print(f"generate_content {model} …", flush=True)
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    t0 = time.time()
    resp = client.models.generate_content(
        model=model,
        contents=[
            {
                "role": "user",
                "parts": [
                    {
                        "text": TEXT,
                        "speech_metadata": {"style": STYLE},
                    }
                ],
            }
        ],
        config={
            "response_modalities": ["AUDIO"],
            "speech_config": {"voice_config": {"voice": "Kore"}},
        },
    )
    data = resp.candidates[0].content.parts[0].inline_data.data
    n = save_audio(OUT / f"am_gen_{model}.wav", data)
    print(f"OK generate {model} bytes={n} sec={time.time()-t0:.1f}", flush=True)


def main() -> None:
    print("key", bool(config.GEMINI_API_KEY), flush=True)
    for model in ("gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts"):
        try:
            try_interactions(model)
            return
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL interactions {model}: {exc}", flush=True)
    for model in ("gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts"):
        try:
            try_generate(model)
            return
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL generate {model}: {exc}", flush=True)
    raise SystemExit("all TTS smoke paths failed")


if __name__ == "__main__":
    main()
