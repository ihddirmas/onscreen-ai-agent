#!/usr/bin/env bash
# Regenerate marketing screenshots from the real Qt overlay (monochrome theme).
set -euo pipefail
cd "$(dirname "$0")/.."
xvfb-run -a python3 scripts/capture_marketing_screenshots.py
