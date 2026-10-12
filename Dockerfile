# Full-Stack OmniStream Media Downloader Dockerfile
FROM python:3.12-slim

# Install system dependencies including FFmpeg and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variables (7860 for Hugging Face, dynamic $PORT for Render/Railway/Koyeb)
ENV PORT=7860
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

EXPOSE 7860 5000 8080

# Run uvicorn server with dynamic port support
CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-7860}"]
