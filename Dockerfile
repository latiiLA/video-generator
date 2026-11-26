# Pipeline worker (FFmpeg + Python). Deploy on Railway/Render — not Vercel.
FROM python:3.12-slim-bookworm

# Bump when deploy must rebuild past a stale image (schema / demo board fixes).
LABEL heritage.worker.rev="2026-03-26-quicktest-6shots"

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
COPY main.py .

ENV PYTHONPATH=/app
ENV OUTPUT_DIR=/app/outputs
ENV RUNS_LOG=/app/runs.jsonl
ENV PORT=8080

RUN mkdir -p /app/outputs /app/cache

EXPOSE 8080
CMD ["python", "main.py"]
