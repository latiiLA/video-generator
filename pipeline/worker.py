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
from pydantic import BaseModel, Field

from pipeline import assemble, config, keyframes, music, narration, script, shots
from pipeline.common import write_json

app = FastAPI(title="Heritage Short Worker", version="0.1.0")


class JobRequest(BaseModel):
    storyline: str = Field(min_length=20, max_length=4000)
    language: str = "am"
    job_id: str | None = None
    storyboard: dict[str, Any] | None = None


class JobStatus(BaseModel):
    id: str
    status: str
    stage: str | None = None
    error: str | None = None
    vertical_url: str | None = None
    horizontal_url: str | None = None


def _job_dir(job_id: str) -> Path:
    d = config.OUTPUT_DIR / "jobs" / job_id
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


def _run_job(job_id: str, body: JobRequest) -> None:
    job_dir = _job_dir(job_id)
    original_out = config.OUTPUT_DIR
    try:
        config.OUTPUT_DIR = job_dir / "outputs"
        config.ensure_dirs()
        sb_path = job_dir / "storyboard.json"

        _set_status(job_id, status="running", stage="script", error=None)
        if body.storyboard:
            write_json(sb_path, body.storyboard)
        else:
            data = script.draft_from_storyline(body.storyline, body.language)
            write_json(sb_path, data)

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
        _set_status(job_id, status="failed", error=str(exc))
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
    import uvicorn

    uvicorn.run("pipeline.worker:app", host="0.0.0.0", port=8080, reload=False)


if __name__ == "__main__":
    main()
