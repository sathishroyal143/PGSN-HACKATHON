# CareBridge — Docker Setup Guide

## Prerequisites

| Tool | Version |
|------|---------|
| Docker Desktop | ≥ 24.x |
| Docker Compose | ≥ v2.x (bundled with Docker Desktop) |

---

## Quick Start (Production-like)

```bash
# 1. Navigate to the project directory
cd CareBridge

# 2. Build images (first time or after code changes)
docker compose build --no-cache

# 3. Start all services in background
docker compose up -d

# 4. Check all services are healthy
docker compose ps

# 5. View backend logs
docker compose logs -f backend
```

The app will be available at **http://localhost**

---

## Services Overview

| Service | Port | Description |
|---------|------|-------------|
| nginx | 80 | Reverse proxy + static file serving |
| backend | 8000 (internal) | Django + Gunicorn + Uvicorn (ASGI) |
| postgres | 5432 (internal) | PostgreSQL 16 database |
| redis | 6379 (internal) | Redis 7 (cache + message broker) |
| celery_worker | — | Background task processor |
| celery_beat | — | Periodic task scheduler |

---

## Common Commands

```bash
# Start services
docker compose up -d

# Stop services (preserves data)
docker compose down

# Stop and remove ALL data (volumes)
docker compose down -v

# Rebuild image after code changes
docker compose build backend

# Apply migrations manually
docker compose exec backend python manage.py migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser

# View logs for all services
docker compose logs -f

# View logs for a specific service
docker compose logs -f backend
docker compose logs -f celery_worker

# Open a shell inside the backend container
docker compose exec backend bash

# Check service health
docker compose ps
```

---

## Development Mode (Hot Reload)

For hot-reloading without rebuilding the image on every code change:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

This mounts your source code into the container while keeping the installed packages intact.

---

## Troubleshooting

### ❌ `exec ./entrypoint.sh: no such file or directory`
**Cause**: Windows CRLF line endings in the shell script.  
**Fix**: The Dockerfile now automatically strips CRLF via `sed`. Rebuild the image:
```bash
docker compose build --no-cache backend
```

### ❌ `DisallowedHost` error
**Cause**: The host header isn't in `ALLOWED_HOSTS`.  
**Fix**: The `.env` now includes `backend` in `ALLOWED_HOSTS`.

### ❌ `Postgres is unavailable` loop
**Cause**: Database not ready before migrations run.  
**Fix**: The healthcheck + `depends_on: condition: service_healthy` ensures proper ordering.

### ❌ `staticfiles` directory error during collectstatic
**Cause**: `STATICFILES_DIRS` referenced `static/` which was empty.  
**Fix**: The Dockerfile now creates the `static/` directory during build.

### ❌ Port 80 already in use
```bash
# Find what's using port 80
netstat -ano | findstr :80
# Change nginx port in docker-compose.yml: "8080:80"
```

### ❌ `celery_worker` starts before migrations complete
**Fix**: The `celery_worker` now depends on `backend: condition: service_started` ensuring Django starts first.

---

## Environment Variables

Key variables in `.env` (do not commit to git):

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | (insecure default) | **Change in production!** |
| `DEBUG` | `True` | Set `False` in production |
| `DB_PASSWORD` | `1407` | PostgreSQL password |
| `GUNICORN_WORKERS` | `4` | Number of Gunicorn worker processes |

---

## Architecture

```
Internet
    │
    ▼
[Nginx :80]
    │
    ├── /static/ → staticfiles volume
    ├── /media/  → media volume
    └── /api/    → [Backend :8000]
                        │
                        ├── [PostgreSQL :5432]
                        ├── [Redis :6379]
                        ├── [Celery Worker]
                        └── [Celery Beat]
```
