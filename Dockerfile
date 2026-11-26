# Pipeline worker (FFmpeg + Python). Deploy on Railway/Render — not Vercel.
FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pipeline ./pipeline
COPY schema ./schema
COPY storyboard.json .
COPY storyboards ./storyboards

ENV PYTHONPATH=/app
ENV OUTPUT_DIR=/app/outputs
ENV RUNS_LOG=/app/runs.jsonl
ENV PORT=8080

RUN mkdir -p /app/outputs /app/cache

EXPOSE 8080
CMD ["sh", "-c", "uvicorn pipeline.worker:app --host 0.0.0.0 --port ${PORT:-8080}"]
