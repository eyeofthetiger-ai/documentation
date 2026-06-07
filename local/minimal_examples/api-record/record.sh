#!/usr/bin/env bash
# Record a 10-second clip from a local EyeOfTheTiger camera, saved as recording.mp4.

curl -fsS -X POST http://eyeofthetiger.local/v1/start > /dev/null
echo "Starting recording for 10 seconds..."
sleep 10
curl -fsS -X POST http://eyeofthetiger.local/v1/stop > /dev/null

curl -fsS http://eyeofthetiger.local/v1/recording -o recording.mp4
echo "Saved recording.mp4"
