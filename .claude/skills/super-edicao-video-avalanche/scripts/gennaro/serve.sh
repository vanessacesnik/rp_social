#!/bin/bash
# Static server for a Gennaro workspace. The element HTML loads /elements, /fonts, /captions,
# /img and /logos as absolute paths from the server root, so the root MUST be the workspace dir.
# Usage: GEN_WORK=/abs/workspace bash serve.sh [PORT]   (PORT default 8100)
# Run it in the background and stop it when the render finishes.
set -e
WORK="${GEN_WORK:-$(pwd)}"
PORT="${1:-8100}"
cd "$WORK"
echo "serving $WORK on http://127.0.0.1:$PORT  (elements -> /elements, fonts -> /fonts)"
exec python3 -m http.server "$PORT" --bind 127.0.0.1
