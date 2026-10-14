#!/usr/bin/env bash
# Grab 3 seconds of the EOT-1's live MJPEG preview (LAN only), saved as stream.mjpg.
# Open the same URL in a browser to watch it. For remote viewing over the
# internet, see cloud/minimal_examples/api-live-stream.

curl -sS --max-time 3 http://eyeofthetiger.local/v1/live-stream.mjpg -o stream.mjpg || true
if [ -s stream.mjpg ]; then
  echo "Saved stream.mjpg ($(wc -c < stream.mjpg) bytes): the preview is streaming"
else
  echo "No data received from /v1/live-stream.mjpg" >&2
  exit 1
fi
