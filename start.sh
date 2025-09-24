#!/usr/bin/env bash
set -euo pipefail

export PGPASSWORD="${POSTGRES_PASSWORD:-}"
export PYTHONPATH="/app:${PYTHONPATH:-}"

mkdir -p /app/generated

# Resolve DB connection envs (only POSTGRES_* vars)
POSTGRES_HOST="${POSTGRES_HOST:-db}"
# В Docker внутренний порт PostgreSQL всегда 5432
POSTGRES_PORT_INTERNAL=5432
POSTGRES_USER="${POSTGRES_USER:-logs}"

# Calculate Gunicorn workers if not provided
if [ -z "${WORKERS:-}" ] || [ "${WORKERS}" = "0" ]; then
  CPU=$(getconf _NPROCESSORS_ONLN || echo 1)
  export WORKERS=$((CPU*2+1))
fi

echo "[start] Waiting for PostgreSQL ${POSTGRES_HOST}:${POSTGRES_PORT_INTERNAL} as ${POSTGRES_USER} ..."
until pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT_INTERNAL}" -U "${POSTGRES_USER}"; do
  sleep 2
done

echo "[start] Running Alembic migrations..."
alembic upgrade head || { echo "[start] Alembic failed, retrying in 5s..."; sleep 5; alembic upgrade head; }

echo "[start] Starting Gunicorn (workers=${WORKERS}) on 0.0.0.0:8000"
exec gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  --workers "${WORKERS}" \
  --bind 0.0.0.0:8000 \
  --forwarded-allow-ips="*" \
  --access-logfile - \
  --error-logfile - \
  --timeout 120
