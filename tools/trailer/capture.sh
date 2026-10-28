#!/bin/sh
# Trailer capture: ./tools/trailer/capture.sh [--survey] [--only id,id] [--fps 60]
# VS Code's terminal exports ELECTRON_RUN_AS_NODE, which would start Electron as plain Node.
cd "$(dirname "$0")/../.." || exit 1
env -u ELECTRON_RUN_AS_NODE node_modules/.bin/electron tools/trailer/capture-main.cjs "$@" 2>&1 | grep -v '^Fontconfig warning'
