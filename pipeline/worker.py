"""HTTP worker that runs the pipeline for web jobs."""

from __future__ import annotations

import json
import shutil
import threading
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator, model_validator

from pipeline import assemble, config, keyframes, music, narration, script, shots
from pipeline.common import load_storyboard, validate_storyboard, write_json
from pipeline.script import _normalize_storyboard

app = FastAPI(title="Heritage Short Worker", version="0.1.0")

# Fixed root so status paths never move when OUTPUT_DIR is swapped per job
JOBS_ROOT = config.ROOT / "outputs" / "jobs"


class JobRequest(BaseModel):
    """Accept a prose storyline and/or a full storyboard.json object.

    Pasting storyboard.json into the UI used to 422 because storyline maxed at 4000
    chars (~8k for our contract). Storyboard-only jobs are valid.
    Set ``demo=True`` for the ~5s UI quick-test storyboard.
    """

    # No Field(min_length=…) — demo / storyboard jobs may send a short placeholder;
    # length is enforced in the model validator only when neither demo nor storyboard is present.
    storyline: str | None = Field(default=None, max_length=20000)
    language: str = "en"
    job_id: str | None = None
    storyboard: dict[str, Any] | None = None
    demo: bool = False

    @field_validator("storyline", mode="before")
    @classmethod
    def _empty_storyline_to_none(cls, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @model_validator(mode="after")
    def _coerce_storyboard_paste(self) -> JobRequest:
        # Demo first so Quick Test never depends on storyline length.
        if self.demo and self.storyboard is None:
            demo_path = config.ROOT / "storyboards" / "demo_5s.json"
            self.storyboard = json.loads(demo_path.read_text(encoding="utf-8"))
            self.storyline = str(
                self.storyboard.get("logline")
                or self.storyboard.get("title")
                or "5-second quick test film for the Heritage Short UI"
            )
            self.language = str(self.storyboard.get("language") or self.language or "en")

        # If the client pasted storyboard JSON into `storyline`, lift it into `storyboard`.
        if self.storyboard is None and self.storyline:
            text = self.storyline.strip()
            if text.startswith("{") and '"shots"' in text:
                try:
                    parsed = json.loads(text)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"storyline looks like JSON but failed to parse: {exc}") from exc
                if isinstance(parsed, dict) and isinstance(parsed.get("shots"), list):
                    self.storyboard = parsed
                    self.storyline = str(
                        parsed.get("logline") or parsed.get("title") or "storyboard.json"
                    )
                    if not self.language or self.language == "en":
                        self.language = str(parsed.get("language") or self.language or "en")

        if self.storyboard is None and (not self.storyline or len(self.storyline.strip()) < 20):
            raise ValueError(
                "Provide a storyline (≥20 chars), demo=true, or a full storyboard object / JSON paste"
            )

        if self.storyboard is not None and (not self.storyline or len(self.storyline.strip()) < 20):
            self.storyline = str(
                self.storyboard.get("logline")
                or self.storyboard.get("title")
                or "storyboard-driven heritage short job"
            )
        return self


class JobStatus(BaseModel):
    id: str
    status: str
    stage: str | None = None
    error: str | None = None
    vertical_url: str | None = None
    horizontal_url: str | None = None


def _job_dir(job_id: str) -> Path:
    d = JOBS_ROOT / job_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _auth(secret: str | None) -> None:
    if secret != config.WORKER_SECRET:
        raise HTTPException(status_code=401, detail="unauthorized")


def _set_status(job_id: str, **fields: Any) -> dict[str, Any]:
    path = _job_dir(job_id) / "status.json"
    data: dict[str, Any] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    data.update(fields)
    data["id"] = job_id
    write_json(path, data)
    return data


def _storyboard_for_job(body: JobRequest, sb_path: Path) -> None:
    """Draft with Gemini, or fall back to repo storyboard when no API key."""
    if body.storyboard:
        data = _normalize_storyboard(dict(body.storyboard))
        validate_storyboard(data)
        write_json(sb_path, data)
        return
    if config.GEMINI_API_KEY:
        data = script.draft_from_storyline(body.storyline or "", body.language)
        write_json(sb_path, data)
        return

    # Offline path without Gemini: reuse committed heritage storyboard
    data = load_storyboard(config.STORYBOARD_PATH)
    data["logline"] = (body.storyline or "heritage short")[:280]
    data["language"] = body.language
    write_json(sb_path, data)


def _run_job(job_id: str, body: JobRequest) -> None:
    job_dir = _job_dir(job_id)
    out_dir = job_dir / "outputs"
    original_out = config.OUTPUT_DIR
    try:
        _set_status(job_id, status="running", stage="script", error=None)
        config.OUTPUT_DIR = out_dir
        config.ensure_dirs()
        sb_path = job_dir / "storyboard.json"

        _storyboard_for_job(body, sb_path)

        _set_status(job_id, stage="narration")
        narration.run(sb_path)

        _set_status(job_id, stage="keyframes")
        keyframes.run(sb_path)

        _set_status(job_id, stage="shots")
        shots.run(sb_path)

        _set_status(job_id, stage="music")
        music.run(sb_path)

        _set_status(job_id, stage="assemble")
        films = assemble.run(sb_path)

        v = job_dir / "final_9x16.mp4"
        h = job_dir / "final_16x9.mp4"
        shutil.copy(films["vertical"], v)
        shutil.copy(films["horizontal"], h)

        _set_status(
            job_id,
            status="ready",
            stage="done",
            vertical_path=str(v),
            horizontal_path=str(h),
        )
    except Exception as exc:  # noqa: BLE001
        _set_status(job_id, status="failed", error=str(exc), stage="failed")
    finally:
        config.OUTPUT_DIR = original_out


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/jobs", response_model=JobStatus)
def create_job(
    body: JobRequest, x_worker_secret: str | None = Header(default=None)
) -> JobStatus:
    _auth(x_worker_secret)
    job_id = body.job_id or uuid.uuid4().hex[:12]
    _set_status(job_id, status="queued", stage="queued", error=None)
    thread = threading.Thread(target=_run_job, args=(job_id, body), daemon=True)
    thread.start()
    return JobStatus(id=job_id, status="queued", stage="queued")


@app.get("/jobs/{job_id}", response_model=JobStatus)
def get_job(
    job_id: str, x_worker_secret: str | None = Header(default=None)
) -> JobStatus:
    _auth(x_worker_secret)
    path = _job_dir(job_id) / "status.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="job not found")
    data = json.loads(path.read_text(encoding="utf-8"))
    ready = data.get("status") == "ready"
    return JobStatus(
        id=job_id,
        status=data.get("status", "unknown"),
        stage=data.get("stage"),
        error=data.get("error"),
        vertical_url=f"/jobs/{job_id}/download?aspect=9x16" if ready else None,
        horizontal_url=f"/jobs/{job_id}/download?aspect=16x9" if ready else None,
    )


@app.get("/jobs/{job_id}/download")
def download(
    job_id: str,
    aspect: str = "9x16",
    x_worker_secret: str | None = Header(default=None),
):
    _auth(x_worker_secret)
    name = "final_9x16.mp4" if aspect == "9x16" else "final_16x9.mp4"
    path = _job_dir(job_id) / name
    if not path.exists():
        raise HTTPException(status_code=404, detail="file not ready")
    return FileResponse(path, media_type="video/mp4", filename=name)


def main() -> None:
    import os

    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("pipeline.worker:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
