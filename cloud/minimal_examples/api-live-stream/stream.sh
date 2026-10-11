#!/usr/bin/env bash
# Start your EOT-1's live stream via the platform and save its WebRTC (WHEP)
# playback URL to whep.txt. Open that URL in a WHEP-capable player to watch.

PORTAL="https://portal-598626659536.europe-west2.run.app"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"
ENV_EXAMPLE="$SCRIPT_DIR/../.env.example"

if [ ! -f "$ENV_FILE" ]; then
  echo "No .env file found. Run: cp $ENV_EXAMPLE $ENV_FILE  then fill in your values."
  exit 1
fi

# shellcheck source=/dev/null
source "$ENV_FILE"

if [[ "$API_KEY" == *REPLACE_ME* || "$CAMERA_ID" == *REPLACE_ME* ]]; then
  echo "Please edit cloud/minimal_examples/.env and replace API_KEY and CAMERA_ID with your values."
  exit 1
fi

API="$PORTAL/api/v1/cameras/$CAMERA_ID"

echo "Starting the live stream..."
curl -fsS -X POST -H "x-api-key: $API_KEY" "$API/live-stream/start" > /dev/null

# The playback URL appears once the stream is up (404 until then).
for _ in $(seq 1 20); do
  if body=$(curl -fsS -H "x-api-key: $API_KEY" "$API/live-stream"); then
    echo "$body" | python3 -c 'import json, sys; print(json.load(sys.stdin)["live_stream"]["webrtc_playback_url"])' > whep.txt
    echo "Saved whep.txt: $(cat whep.txt)"
    echo "Stop it when done: curl -X POST -H \"x-api-key: \$API_KEY\" $API/live-stream/stop"
    exit 0
  fi
  sleep 1
done
echo "The live stream did not come up within 20 seconds." >&2
exit 1
