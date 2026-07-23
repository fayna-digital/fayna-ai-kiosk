#!/bin/bash
# AI Kiosk — launcher
# Requires a Python 3.11 venv with piper-tts, vosk, pyaudio, Pillow installed.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

VENV="$SCRIPT_DIR/venv"

source "$VENV/bin/activate" 2>/dev/null || {
    echo "[ERROR] venv not found. Run setup first:"
    echo "  python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
}

python3 -m src.main
