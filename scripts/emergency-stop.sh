#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo " SPOT EMERGENCY STOP"
echo "========================================"
echo

echo "Activating SPOT emergency stop..."

# Stop the normal SPOT service first.
systemctl stop spot.service 2>/dev/null || true

# Prevent the timer from starting SPOT again.
systemctl stop spot.timer 2>/dev/null || true

# Use the SPOT CLI emergency-stop mechanism when available.
if command -v spot >/dev/null 2>&1; then
    spot emergency-stop 2>/dev/null || true
else
    python3 -m spot emergency-stop 2>/dev/null || true
fi

# Stop the emergency service if it exists.
systemctl stop spot-emergency.service 2>/dev/null || true

echo
echo "SPOT emergency stop requested."
echo
echo "Normal activity should remain disabled until the emergency"
echo "stop state is explicitly reset."
echo
echo "Check status with:"
echo "  ./scripts/status.sh"
echo
echo "After the cause has been resolved, reset with:"
echo "  spot reset-emergency-stop"
echo "========================================"
