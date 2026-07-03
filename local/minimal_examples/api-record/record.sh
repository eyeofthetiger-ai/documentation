#!/usr/bin/env bash
# Record a 10-second clip from a local EyeOfTheTiger camera, saved as recording.mp4.

curl -fsS "http://eyeofthetiger.local/v1/clip?duration_s=10" -o recording.mp4
echo "Saved recording.mp4"
