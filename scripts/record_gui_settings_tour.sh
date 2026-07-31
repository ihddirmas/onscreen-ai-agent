#!/usr/bin/env bash
# Record full Settings + feature guide tour (all GUI settings sections).
set -euo pipefail
cd /workspace

if [[ -f .env.test ]]; then
  bash scripts/start_local_e2e_stack.sh 2>/dev/null || true
fi

pkill -f 'Xvfb :99' 2>/dev/null || true
sleep 1
Xvfb :99 -screen 0 1280x720x24 -ac &
XVFB_PID=$!
sleep 2
export DISPLAY=:99

OUT="/opt/cursor/artifacts/oncue-settings-feature-tour.mp4"
# ~3.5s guide + 6 sections (~16s) + onboarding ≈ 24s
ffmpeg -y -video_size 1280x720 -framerate 10 -f x11grab -i :99.0 -t 26 \
  "$OUT" &
FFPID=$!
sleep 1
.venv/bin/python scripts/demo_gui_settings_tour.py
wait "$FFPID" || true
kill "$XVFB_PID" 2>/dev/null || true
ls -la "$OUT"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$OUT"
