# ============================================================
# Sofia – Chainlit Frontend  (multi-stage, Alpine, non-root)
# ============================================================

# ── Stage 1: dependency builder ─────────────────────────────
FROM python:3.12-alpine AS builder

# Build-time system deps (gcc / musl-dev needed for some wheels)
RUN apk add --no-cache gcc musl-dev libffi-dev

WORKDIR /build

COPY requirements.txt .

# Install into a local prefix so the runtime stage can copy only the wheels
RUN pip install --user --no-cache-dir -r requirements.txt

# ── Stage 2: production runtime ─────────────────────────────
FROM python:3.12-alpine

LABEL maintainer="ItalianOllama Team"
LABEL description="Sofia – Chainlit-based Italian Tutor chat interface"

# Runtime system deps
RUN apk add --no-cache curl

WORKDIR /app

# Security: non-root user
RUN addgroup -S chainlit && adduser -S -G chainlit chainlit

# Copy installed Python packages from the builder stage
COPY --from=builder /root/.local /home/chainlit/.local

# Copy application source
COPY config.py       ./config.py
COPY api/            ./api/
COPY chainlit_app.py ./chainlit_app.py

# Make frontend importable as a package
RUN touch __init__.py

# Environment
ENV PATH=/home/chainlit/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    # Chainlit ships its own static files; override the host/port here if needed
    CHAINLIT_HOST=0.0.0.0 \
    CHAINLIT_PORT=8501

# Hand off ownership and switch to the non-root user
RUN chown -R chainlit:chainlit /app
USER chainlit

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

CMD ["chainlit", "run", "chainlit_app.py", "--host", "0.0.0.0", "--port", "8501"]
