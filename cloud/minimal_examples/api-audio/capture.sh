#!/usr/bin/env bash
# Record a 10-second audio clip from your EOT-1's USB microphone via the platform, saved as recording.aac.
# Returns 503 if no microphone is attached (check microphone.connected in GET .../status).

PORTAL="https://platform.eyeofthetiger.ai"

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

echo "Recording an audio clip..."
curl -fsSL -H "x-api-key: $API_KEY" "$API/audio/clip?duration_s=10" -o recording.aac
echo "Saved recording.aac"
