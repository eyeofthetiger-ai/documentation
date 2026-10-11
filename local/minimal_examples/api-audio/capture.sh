#!/usr/bin/env bash
# Record a 10-second audio clip from the EOT-1's USB microphone, saved as recording.aac.
# Returns 503 if no microphone is attached (check microphone.connected in GET /v1/status).

curl -fsS "http://eyeofthetiger.local/v1/audio/clip?duration_s=10" -o recording.aac
echo "Saved recording.aac"
