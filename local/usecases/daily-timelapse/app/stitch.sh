#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXAMPLE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DATE="${1:-$(date -d yesterday +%Y-%m-%d)}"
FRAMES_DIR="$EXAMPLE_DIR/output/frames/$DATE"
OUTPUT_DIR="$EXAMPLE_DIR/output/timelapse"
OUTPUT_FILE="$OUTPUT_DIR/$DATE.mp4"

if [[ ! -d "$FRAMES_DIR" ]]; then
    echo "No frames directory found for $DATE: $FRAMES_DIR" >&2
    exit 1
fi

FRAME_COUNT=$(find "$FRAMES_DIR" -name '*.jpg' | wc -l)
if [[ "$FRAME_COUNT" -eq 0 ]]; then
    echo "No frames found in $FRAMES_DIR" >&2
    exit 1
fi

echo "Stitching $FRAME_COUNT frames for $DATE..."

mkdir -p "$OUTPUT_DIR"

# Write a sorted file list for ffmpeg to guarantee chronological order
FILE_LIST=$(mktemp)
trap 'rm -f "$FILE_LIST"' EXIT
find "$FRAMES_DIR" -name '*.jpg' | sort | while read -r f; do
    echo "file '$f'"
done > "$FILE_LIST"

ffmpeg -y -f concat -safe 0 -i "$FILE_LIST" -framerate 24 -c:v libx264 -pix_fmt yuv420p "$OUTPUT_FILE"

echo "Timelapse saved: $OUTPUT_FILE"
