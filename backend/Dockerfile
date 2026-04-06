# ---------------------------------------------------------------------------
# Multi-stage Dockerfile — Production-grade Django
# ---------------------------------------------------------------------------

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: Runtime
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r django && useradd -r -g django django

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy project code
COPY . .

# Create directories for logs and static files
RUN mkdir -p /app/logs /app/staticfiles \
    && chown -R django:django /app

# Collect static files
RUN DJANGO_SETTINGS_MODULE=app.settings.production \
    SECRET_KEY=build-placeholder \
    python manage.py collectstatic --noinput 2>/dev/null || true

# Switch to non-root user
USER django

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "app.wsgi:application"]
