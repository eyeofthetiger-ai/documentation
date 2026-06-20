#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXAMPLE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DATE_DIR="$EXAMPLE_DIR/output/frames/$(date +%Y-%m-%d)"
OUTPUT_FILE="$DATE_DIR/$(date +%H-%M).jpg"

mkdir -p "$DATE_DIR"
curl -sf "http://eyeofthetiger.local/snapshot" -o "$OUTPUT_FILE"
echo "Saved: $OUTPUT_FILE"
