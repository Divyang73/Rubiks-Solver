#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8001}"
PID="$(netstat -tulpn 2>/dev/null | awk -v p=":${PORT} " '$0 ~ p {print $7}' | cut -d/ -f1 | head -n1)"

if [[ -n "${PID:-}" ]]; then
  echo "Stopping existing backend on port ${PORT} (PID ${PID})"
  kill "${PID}" || true
  sleep 1
fi

echo "Starting backend on port ${PORT}"
python server.py
