#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ ! -d .venv ]; then
  python3.13 -m venv .venv
fi
.venv/bin/pip install -q -r requirements.txt
npm ci --silent
npm run build
.venv/bin/python backend/manage.py migrate
exec .venv/bin/python backend/manage.py runserver 127.0.0.1:8000
