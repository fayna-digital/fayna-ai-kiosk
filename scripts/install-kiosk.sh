#!/bin/bash
# Install AI Kiosk as a systemd service (Linux / Raspberry Pi).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Installing AI Kiosk systemd service..."

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

cp "$SCRIPT_DIR/ai-kiosk.service" /etc/systemd/system/
echo "Service file copied"

systemctl daemon-reload
echo "Systemd reloaded"

systemctl enable ai-kiosk
echo "Service enabled for auto-start"

systemctl start ai-kiosk
echo "Service started"

sleep 2
systemctl status ai-kiosk --no-pager

echo ""
echo "Repository: $REPO_ROOT"
echo "Logs:  sudo journalctl -u ai-kiosk -f"
echo "Stop:  sudo systemctl stop ai-kiosk"
echo "Disable: sudo systemctl disable ai-kiosk"
