#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
ZIP="${1:-meridium_chess_assets.zip}"
if [[ ! -f "$ZIP" ]]; then
  echo "Usage: $0 path/to/meridium_chess_assets.zip"
  exit 1
fi
unzip -o "$ZIP" -d "$ROOT"
echo "Installed chess_widget.html + soju/ into $ROOT"
ls -la "$ROOT/chess_widget.html" "$ROOT/soju/"
