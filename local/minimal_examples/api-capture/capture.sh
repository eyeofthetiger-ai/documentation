#!/usr/bin/env bash
# Capture a still image from a local EyeOfTheTiger camera, saved as image.jpg.

curl -fsS http://eyeofthetiger.local/v1/snapshot -o image.jpg
echo "Saved image.jpg"
