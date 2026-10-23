#!/bin/sh
set -eu
cd "$(dirname "$0")/.."

PYTHON_BIN=python3.13
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN=python3
fi

if [ ! -d .venv ]; then
  "$PYTHON_BIN" -m venv .venv
fi

.venv/bin/pip install -q -r requirements.txt
npm ci --silent
npm run build
.venv/bin/python backend/manage.py migrate
exec .venv/bin/python backend/manage.py runserver 127.0.0.1:8000
