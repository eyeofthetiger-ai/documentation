#!/usr/bin/env bash
# Record a 5-second clip from your camera via the platform, saved as recording.mp4.

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

echo "Recording a clip..."
curl -fsS -H "x-api-key: $API_KEY" -X POST "$API/start" > /dev/null
sleep 10
curl -fsS -H "x-api-key: $API_KEY" -X POST "$API/stop" > /dev/null

sleep 3  # give the clip a moment to upload
curl -fsSL -H "x-api-key: $API_KEY" "$API/recording" -o recording.mp4
echo "Saved recording.mp4"
