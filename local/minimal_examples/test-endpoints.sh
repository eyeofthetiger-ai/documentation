#!/usr/bin/env bash
#
# Minimal endpoint test for a LOCAL EyeOfTheTiger camera.
#
# Talks straight to the device on your network — no account or API key. It
# captures a still, records a short clip, and opens the live stream, opening
# each result so you can confirm it works end to end.
#
# Usage:
#   ./test-endpoints.sh
#   BASE=http://192.168.1.50:8000/v1 RECORD_SECONDS=8 ./test-endpoints.sh
#
set -euo pipefail

BASE="${BASE:-http://eyeofthetiger.local/v1}"
RECORD_SECONDS="${RECORD_SECONDS:-5}"
OUT="$(mktemp -d)"

# Open a file (or URL) with the OS default handler.
open_target() {
  if command -v xdg-open >/dev/null 2>&1; then xdg-open "$1" >/dev/null 2>&1 &
  elif command -v open >/dev/null 2>&1; then open "$1";
  else echo "  open manually: $1"; fi
}

# Retry GET /recording until the clip is ready (the device finalises on stop).
fetch_recording() {
  for _ in $(seq 1 15); do
    if curl -fsS "$BASE/recording" -o "$OUT/recording.mp4" 2>/dev/null; then return 0; fi
    sleep 2
  done
  return 1
}

echo "Device: $BASE"
echo "Output: $OUT"

echo
echo "1/3  Snapshot  →  GET /image"
curl -fsS "$BASE/image" -o "$OUT/image.jpg"
echo "     saved image.jpg ($(wc -c < "$OUT/image.jpg") bytes)"
open_target "$OUT/image.jpg"

echo
echo "2/3  Recording →  POST /start, wait ${RECORD_SECONDS}s, POST /stop, GET /recording"
curl -fsS -X POST "$BASE/start" >/dev/null
sleep "$RECORD_SECONDS"
curl -fsS -X POST "$BASE/stop" >/dev/null
if fetch_recording; then
  echo "     saved recording.mp4 ($(wc -c < "$OUT/recording.mp4") bytes)"
  open_target "$OUT/recording.mp4"
else
  echo "     recording not ready in time"
fi

echo
echo "3/3  Live stream → GET /stream (opening in browser)"
open_target "$BASE/stream"

echo
echo "Done. Files in $OUT"
