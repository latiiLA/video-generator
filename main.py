"""Railway/Railpack entrypoint — exposes the FastAPI worker app."""

from pipeline.worker import app

__all__ = ["app"]


if __name__ == "__main__":
    import os

    import uvicorn

    uvicorn.run(
        "pipeline.worker:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
    )
