"""REST TTS smoke with hard HTTP timeout."""
from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
KEY = os.getenv("GEMINI_API_KEY", "")
OUT = ROOT / "outputs" / "debug"
OUT.mkdir(parents=True, exist_ok=True)

TEXT = "በሰባተኛ ክፍል ነበርኩ ለመጀመሪያ ጊዜ የአያቴን የገጠር ቤት ስጎበኝ።"
STYLE = "warm, nostalgic, unhurried"


def try_generate(model: str) -> None:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": TEXT, "speechMetadata": {"style": STYLE}}],
            }
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"voice": "Kore"}},
        },
    }
    print(f"REST generate {model} …", flush=True)
    t0 = time.time()
    r = requests.post(
        url,
        params={"key": KEY},
        headers={"Content-Type": "application/json"},
        data=json.dumps(body),
        timeout=60,
    )
    print(f"status={r.status_code} sec={time.time()-t0:.1f}", flush=True)
    if not r.ok:
        print(r.text[:500], flush=True)
        r.raise_for_status()
    payload = r.json()
    data_b64 = payload["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
    raw = base64.b64decode(data_b64)
    path = OUT / f"am_rest_{model}.wav"
    if raw[:4] == b"RIFF":
        path.write_bytes(raw)
    else:
        import wave

        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(raw)
    print(f"OK {path} bytes={path.stat().st_size}", flush=True)


def try_interactions(model: str) -> None:
    url = "https://generativelanguage.googleapis.com/v1beta/interactions"
    body = {
        "model": model,
        "input": [
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
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": "Kore"}]},
    }
    print(f"REST interactions {model} …", flush=True)
    t0 = time.time()
    r = requests.post(
        url,
        params={"key": KEY},
        headers={"Content-Type": "application/json"},
        data=json.dumps(body),
        timeout=60,
    )
    print(f"status={r.status_code} sec={time.time()-t0:.1f}", flush=True)
    if not r.ok:
        print(r.text[:800], flush=True)
        r.raise_for_status()
    payload = r.json()
    audio = (payload.get("output_audio") or {}).get("data")
    if not audio:
        for step in payload.get("steps") or []:
            for part in step.get("content") or []:
                if part.get("data"):
                    audio = part["data"]
                    break
    if not audio:
        raise RuntimeError(f"no audio keys={list(payload.keys())}")
    path = OUT / f"am_rest_inter_{model}.wav"
    path.write_bytes(base64.b64decode(audio))
    print(f"OK {path} bytes={path.stat().st_size}", flush=True)


def main() -> None:
    print("key", bool(KEY), flush=True)
    errors = []
    for model in ("gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts"):
        try:
            try_interactions(model)
            return
        except Exception as exc:  # noqa: BLE001
            errors.append(f"inter:{model}:{exc}")
            print("FAIL", errors[-1], flush=True)
    for model in ("gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts"):
        try:
            try_generate(model)
            return
        except Exception as exc:  # noqa: BLE001
            errors.append(f"gen:{model}:{exc}")
            print("FAIL", errors[-1], flush=True)
    raise SystemExit("; ".join(errors))


if __name__ == "__main__":
    main()
