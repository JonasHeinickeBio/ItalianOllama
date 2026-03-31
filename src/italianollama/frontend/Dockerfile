# ============================================================
# Sofia – Chainlit Frontend (Alpine, non-root, simplified)
# ============================================================
FROM python:3.12-alpine

LABEL maintainer="ItalianOllama Team"
LABEL description="Sofia – Chainlit-based Italian Tutor chat interface"

# Runtime system deps (curl for health check)
RUN apk add --no-cache curl gcc musl-dev libffi-dev

# Create and set permissions on /app directory
RUN mkdir -p /app && chmod 777 /app

WORKDIR /app

# Copy requirements from backend and install directly with pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir chainlit>=2.0.0 sniffio

# Copy entire src/italianollama package
COPY src/italianollama ./src/italianollama

# Set Python path
ENV PYTHONPATH=/app/src

# Health check - verify imports work
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "from italianollama.frontend import config, api, ui; print('OK')" || exit 1

# Run Chainlit app (as root for now to avoid permission issues)
CMD ["chainlit", "run", "src/italianollama/frontend/chainlit_app.py", "--host", "0.0.0.0", "--port", "8501"]
