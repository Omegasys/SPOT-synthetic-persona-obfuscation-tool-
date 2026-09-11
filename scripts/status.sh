#!/usr/bin/env bash
set -euo pipefail

SERVICE="spot.service"

echo "========================================"
echo " SPOT Status"
echo "========================================"
echo

if systemctl is-active --quiet "${SERVICE}"; then
    echo "Service:       ACTIVE"
else
    echo "Service:       INACTIVE"
fi

if systemctl is-enabled --quiet "${SERVICE}" 2>/dev/null; then
    echo "Autostart:     ENABLED"
else
    echo "Autostart:     DISABLED"
fi

if systemctl is-active --quiet spot.timer 2>/dev/null; then
    echo "Timer:         ACTIVE"
else
    echo "Timer:         INACTIVE"
fi

echo
echo "Systemd status:"
echo "----------------------------------------"

systemctl status "${SERVICE}" \
    --no-pager \
    --lines=10 \
    2>/dev/null || true

echo
echo "SPOT CLI status:"
echo "----------------------------------------"

if command -v spot >/dev/null 2>&1; then
    spot status 2>/dev/null || true
else
    python3 -m spot status 2>/dev/null || true
fi

echo
echo "Directories:"
echo "----------------------------------------"
echo "Configuration: /etc/spot"
echo "Data:          /var/lib/spot"
echo "Logs:          /var/log/spot"
echo "Runtime:       /run/spot"
echo

echo "========================================"
