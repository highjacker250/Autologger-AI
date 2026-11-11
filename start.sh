#!/usr/bin/env bash
set -euo pipefail
: "${PORT:=10000}"
export PORT
python -m uvicorn main:app --host 0.0.0.0 --port "$PORT" &
WEB_PID=$!
BOT_PID=""
cleanup() {
  kill "$WEB_PID" 2>/dev/null || true
  if [[ -n "$BOT_PID" ]]; then kill "$BOT_PID" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM
if [[ -n "${BOT_TOKEN:-}" ]]; then
  python bot.py &
  BOT_PID=$!
  wait -n "$WEB_PID" "$BOT_PID"
else
  echo "BOT_TOKEN not set; starting web monitor only."
  wait "$WEB_PID"
fi
