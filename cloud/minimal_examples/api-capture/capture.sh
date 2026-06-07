#!/usr/bin/env bash
# Capture a still image from your camera via the platform, saved as image.jpg.
# Edit the three values below first.

PORTAL="https://portal-598626659536.europe-west2.run.app"
API_KEY="eott_REPLACE_ME"
CAMERA_ID="cam_REPLACE_ME"

curl -fsSL -H "x-api-key: $API_KEY" \
  "$PORTAL/api/v1/cameras/$CAMERA_ID/image" -o image.jpg
echo "Saved image.jpg"
