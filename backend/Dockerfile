# Backend Dockerfile - Italian Tutor API (Production-Ready)
FROM python:3.12-slim-bookworm AS builder

# Build stage - compile dependencies
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================
# Production stage - minimal runtime
# ============================================
FROM python:3.12-slim-bookworm

LABEL maintainer="ItalianOllama Team"
LABEL description="Italian Language Learning API with streaming"

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Security: Create non-root user
RUN groupadd -r apiuser && useradd -r -g apiuser apiuser

# Copy Python packages from builder
COPY --from=builder /root/.local /home/apiuser/.local

# Copy source code
COPY src /app/src

# Set environment
ENV PATH=/home/apiuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
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
