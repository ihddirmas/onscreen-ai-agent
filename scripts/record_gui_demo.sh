#!/usr/bin/env bash
set -euo pipefail
cd /workspace
pkill -f 'Xvfb :99' 2>/dev/null || true
sleep 1
Xvfb :99 -screen 0 1280x720x24 -ac &
XVFB_PID=$!
sleep 2
export DISPLAY=:99
ffmpeg -y -video_size 1280x720 -framerate 10 -f x11grab -i :99.0 -t 15 \
  /opt/cursor/artifacts/oncue-desktop-gui-demo.mp4 &
FFPID=$!
sleep 1
.venv/bin/python scripts/demo_gui_flow.py
wait "$FFPID" || true
kill "$XVFB_PID" 2>/dev/null || true
ls -la /opt/cursor/artifacts/oncue-desktop-gui-demo.mp4
