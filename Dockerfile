# ══════════════════════════════════════════════════════════════════════
# HotGigs 2026 - Enterprise HR Automation Platform
# Multi-stage Docker build for production deployment
# ══════════════════════════════════════════════════════════════════════

# ── Stage 1: Builder ─────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a virtual env
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements-docker.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements-docker.txt

# ── Stage 2: Production ─────────────────────────────────────────────
FROM python:3.12-slim AS production

LABEL maintainer="pratap@businessintelli.com"
LABEL description="HotGigs 2026 - Enterprise HR Automation Platform"
LABEL version="2.0.0"

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Environment configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash hotgigs && \
    chown -R hotgigs:hotgigs /app && \
    mkdir -p /app/data /app/logs /app/uploads && \
    chown -R hotgigs:hotgigs /app/data /app/logs /app/uploads

USER hotgigs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

# Entrypoint
COPY docker-entrypoint.sh /docker-entrypoint.sh
USER root
RUN chmod +x /docker-entrypoint.sh
USER hotgigs

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--loop", "uvloop"]

# ── Stage 3: Development ────────────────────────────────────────────
FROM production AS development

USER root
RUN pip install --no-cache-dir \
    black \
    flake8 \
    mypy \
    ipython \
    debugpy
USER hotgigs

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
