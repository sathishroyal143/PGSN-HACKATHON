# ==============================================================================
# Builder Stage — compile Python wheels
# ==============================================================================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Build-time system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /wheels

COPY requirements.txt .

# Build all dependency wheels
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ==============================================================================
# Final Stage — lean runtime image
# ==============================================================================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# Runtime system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR $APP_HOME

# Install Python packages from wheels (no network access needed)
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*.whl \
    && rm -rf /wheels

# Create runtime directories with correct ownership
RUN mkdir -p $APP_HOME/staticfiles $APP_HOME/media $APP_HOME/logs \
    $APP_HOME/static \
    && chown -R appuser:appgroup $APP_HOME

# Copy application source code
COPY --chown=appuser:appgroup . $APP_HOME/

# Fix line endings and make shell scripts executable (handles Windows CRLF)
RUN find $APP_HOME -name "*.sh" -exec sed -i 's/\r$//' {} \; \
    && chmod +x $APP_HOME/entrypoint.sh $APP_HOME/healthcheck.sh

# Switch to non-root user
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

ENTRYPOINT ["./entrypoint.sh"]
