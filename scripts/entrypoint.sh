#!/usr/bin/env bash
set -euo pipefail

exec tini -s -- bash -c '
  alembic upgrade head
  gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000 --timeout 180 --log-level info
'
