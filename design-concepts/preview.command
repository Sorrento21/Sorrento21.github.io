#!/bin/bash
# Double-click this file in Finder to preview the design concepts.
# It serves the whole website/ folder (so ../src/images resolves) and opens the chooser.
cd "$(dirname "$0")/.." || exit 1

PORT=8899
while lsof -i :$PORT >/dev/null 2>&1; do PORT=$((PORT+1)); done

echo "Serving $(pwd) at http://localhost:$PORT"
echo "Chooser: http://localhost:$PORT/design-concepts/index.html"
echo "Press Ctrl-C in this window to stop."

python3 -m http.server "$PORT" >/dev/null 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null' EXIT

sleep 1
open "http://localhost:$PORT/design-concepts/index.html"
wait $SERVER_PID
