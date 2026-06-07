#!/usr/bin/env bash
# Record a 5-second clip from your camera via the platform, saved as recording.mp4.
# Edit the three values below first.

PORTAL="https://portal-598626659536.europe-west2.run.app"
API_KEY="eott_REPLACE_ME"
CAMERA_ID="cam_REPLACE_ME"
API="$PORTAL/api/v1/cameras/$CAMERA_ID"

curl -fsS -H "x-api-key: $API_KEY" -X POST "$API/start" > /dev/null
sleep 5
curl -fsS -H "x-api-key: $API_KEY" -X POST "$API/stop" > /dev/null

sleep 3  # give the clip a moment to upload
curl -fsSL -H "x-api-key: $API_KEY" "$API/recording" -o recording.mp4
echo "Saved recording.mp4"
