# syntax=docker/dockerfile:1
# ClaimSense AI — Production Hardened Multi-Stage Dockerfile
# Milestone: Phase 11 Production Containerization

FROM python:3.11-slim-bookworm AS base

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_DEBUG=0 \
    PORT=5001 \
    HOST=0.0.0.0

WORKDIR /app

# Install system dependencies: Tesseract OCR, OpenCV runtime libraries, curl for healthchecks
RUN apt-get update && apt-get install --no-install-recommends -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated unprivileged user for security isolation
RUN groupadd -g 10001 claimsense && \
    useradd -u 10001 -g claimsense -s /bin/bash -m claimsense

# Copy dependency manifests
COPY requirements.txt ./

# Install Python production dependencies and WSGI servers
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir waitress gunicorn

# Copy application source code and configurations
COPY backend ./backend
COPY frontend ./frontend
COPY models ./models
COPY scripts ./scripts
COPY wsgi.py ./

# Create runtime directories with appropriate non-root ownership
RUN mkdir -p data uploads reports backups && \
    chown -R claimsense:claimsense /app

# Switch to unprivileged user
USER claimsense

# Expose internal application port
EXPOSE 5001

# Health check probe against the lightweight health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:5001/api/health || exit 1

# Launch production WSGI runner
CMD ["python", "scripts/serve_production.py", "--host", "0.0.0.0", "--port", "5001", "--server", "auto"]
