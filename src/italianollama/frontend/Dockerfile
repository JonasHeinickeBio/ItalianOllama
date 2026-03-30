# ============================================================
# Sofia – Chainlit Frontend (Alpine, non-root, simplified)
# ============================================================
FROM python:3.12-alpine

LABEL maintainer="ItalianOllama Team"
LABEL description="Sofia – Chainlit-based Italian Tutor chat interface"

# Runtime system deps (curl for health check)
RUN apk add --no-cache curl gcc musl-dev libffi-dev

WORKDIR /app

# Security: non-root user
RUN addgroup -S chainlit && adduser -S -G chainlit chainlit

# Copy requirements from backend and install directly with pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire src/italianollama package
COPY --chown=chainlit:chainlit src/italianollama ./src/italianollama

# Set Python path
ENV PYTHONPATH=/app/src

# Change to Chainlit user
USER chainlit

# Health check - verify imports work
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "from italianollama.frontend import config, api, ui; print('OK')" || exit 1

# Run Chainlit app
CMD ["chainlit", "run", "src/italianollama/frontend/chainlit_app.py", "--host", "0.0.0.0", "--port", "8501"]
