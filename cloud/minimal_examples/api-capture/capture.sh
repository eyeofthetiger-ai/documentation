#!/usr/bin/env bash
# Capture a still image from your camera via the platform, saved as image.jpg.

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

curl -fsSL -H "x-api-key: $API_KEY" \
  "$PORTAL/api/v1/cameras/$CAMERA_ID/image" -o image.jpg
echo "Saved image.jpg"
