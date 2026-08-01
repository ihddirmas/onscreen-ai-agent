#!/usr/bin/env bash
# Record OnCUE homepage scroll tour (v0-import design on Next.js).
set -euo pipefail
cd /workspace/website

OUT_DIR="/opt/cursor/artifacts"
mkdir -p "$OUT_DIR"

npx playwright test e2e/homepage-tour.spec.ts --project=chromium 2>&1

WEBM=$(find test-results -name "video.webm" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
MP4="$OUT_DIR/oncue-website-homepage-v0.mp4"

if [[ -n "${WEBM:-}" && -f "$WEBM" ]]; then
  ffmpeg -y -i "$WEBM" -c:v libx264 -pix_fmt yuv420p -movflags +faststart "$MP4" 2>/dev/null
  ls -la "$MP4"
  ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$MP4" 2>/dev/null || true
else
  echo "No playwright video found"
  exit 1
fi

npx playwright test e2e/smoke.spec.ts --project=chromium
