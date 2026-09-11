#!/usr/bin/env bash
set -euo pipefail

SERVICE="spot.service"

echo "Stopping SPOT..."

if [[ "${EUID}" -eq 0 ]]; then
    systemctl stop "${SERVICE}"
else
    systemctl --user stop "${SERVICE}" 2>/dev/null || {
        echo "Error: stopping the system SPOT service requires root privileges."
        echo "Try:"
        echo "  sudo ./scripts/stop.sh"
        exit 1
    }
fi

echo
echo "SPOT stopped."
