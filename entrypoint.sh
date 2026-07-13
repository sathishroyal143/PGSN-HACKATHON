#!/bin/bash
set -e

echo "================================================="
echo " CareBridge Backend Starting..."
echo "================================================="

# ── Wait for PostgreSQL to be reachable ───────────────────────────────────────
echo "[1/4] Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."
until python -c "
import socket, sys
try:
    s = socket.create_connection(('${DB_HOST:-postgres}', int('${DB_PORT:-5432}')), timeout=2)
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
  echo "      Postgres unavailable - retrying in 2s..."
  sleep 2
done
echo "      Postgres is up!"

# ── Apply database migrations ─────────────────────────────────────────────────
echo "[2/4] Applying database migrations..."
python manage.py migrate --noinput

# ── Collect static files ──────────────────────────────────────────────────────
echo "[3/4] Collecting static files..."
python manage.py collectstatic --noinput --clear

# ── Start Gunicorn + Uvicorn (ASGI) ──────────────────────────────────────────
echo "[4/4] Starting Gunicorn with Uvicorn workers..."
exec gunicorn config.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-4} \
    --timeout 120 \
    --keep-alive 5 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
