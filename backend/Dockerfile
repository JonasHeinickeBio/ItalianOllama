# Backend Dockerfile - Italian Tutor API (Production-Ready)
FROM python:3.12-slim-bookworm

LABEL maintainer="ItalianOllama Team"
LABEL description="Italian Language Learning API with streaming"

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 --retries=5 -r requirements.txt || \
    pip install --no-cache-dir --default-timeout=100 --retries=5 -r requirements.txt

# Security: Create non-root user
RUN groupadd -r apiuser && useradd -r -g apiuser apiuser

# Copy source code  and set ownership
COPY --chown=apiuser:apiuser src /app/src

# Set environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# Switch to non-root user
USER apiuser

EXPOSE 8000

# Health check with timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with gunicorn for production
CMD ["uvicorn", "italianollama.api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--log-level", "info"]
