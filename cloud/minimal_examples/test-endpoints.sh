#!/usr/bin/env bash
#
# Minimal endpoint test for the EyeOfTheTiger CLOUD platform (developer API).
#
# Captures a still, records a short clip, and checks the live stream — all
# through the platform with your developer API key. Snapshot and recording
# follow the platform's redirect to a signed storage URL.
#
# Set these first (API_KEY and CAMERA_ID are required):
#   export API_KEY=eott_xxxxxxxx
#   export CAMERA_ID=cam_xxxxxxxx
#   ./test-endpoints.sh
#
set -euo pipefail

PORTAL_URL="${PORTAL_URL:-https://portal-598626659536.europe-west2.run.app}"
API_KEY="${API_KEY:?Set API_KEY to your eott_ developer key (from the portal Settings page)}"
CAMERA_ID="${CAMERA_ID:?Set CAMERA_ID to your camera id}"
RECORD_SECONDS="${RECORD_SECONDS:-5}"
OUT="$(mktemp -d)"

API="$PORTAL_URL/api/v1/cameras/$CAMERA_ID"
AUTH=(-H "x-api-key: $API_KEY")

open_target() {
  if command -v xdg-open >/dev/null 2>&1; then xdg-open "$1" >/dev/null 2>&1 &
  elif command -v open >/dev/null 2>&1; then open "$1";
  else echo "  open manually: $1"; fi
}

# Recording finalises asynchronously in the cloud, so poll until it's ready.
fetch_recording() {
  for _ in $(seq 1 20); do
    if curl -fsSL "${AUTH[@]}" "$API/recording" -o "$OUT/recording.mp4" 2>/dev/null; then return 0; fi
    sleep 2
  done
  return 1
}

echo "Platform: $PORTAL_URL"
echo "Camera:   $CAMERA_ID"
echo "Output:   $OUT"

echo
echo "1/3  Snapshot  →  GET /image  (follows 302 to signed storage URL)"
curl -fsSL "${AUTH[@]}" "$API/image" -o "$OUT/image.jpg"
echo "     saved image.jpg ($(wc -c < "$OUT/image.jpg") bytes)"
open_target "$OUT/image.jpg"

echo
echo "2/3  Recording →  POST /start, wait ${RECORD_SECONDS}s, POST /stop, GET /recording"
curl -fsS "${AUTH[@]}" -X POST "$API/start" >/dev/null
sleep "$RECORD_SECONDS"
curl -fsS "${AUTH[@]}" -X POST "$API/stop" >/dev/null
if fetch_recording; then
  echo "     saved recording.mp4 ($(wc -c < "$OUT/recording.mp4") bytes)"
  open_target "$OUT/recording.mp4"
else
  echo "     recording not ready in time"
fi

echo
echo "3/3  Live stream → GET /stream"
# The API stream needs the x-api-key header, so a browser can't open it directly.
# Confirm bytes flow with curl, then open the dashboard for the visual preview
# (it streams over the logged-in session).
echo "     checking 3s of MJPEG..."
curl -fsS "${AUTH[@]}" --max-time 3 "$API/stream" -o "$OUT/stream.mjpeg" 2>/dev/null || true
echo "     received $(wc -c < "$OUT/stream.mjpeg" 2>/dev/null || echo 0) bytes"
echo "     opening dashboard preview in browser (sign in to view)..."
open_target "$PORTAL_URL/cameras/$CAMERA_ID"

echo
echo "Done. Files in $OUT"
