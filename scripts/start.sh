#!/usr/bin/env bash
set -euo pipefail

SERVICE="spot.service"

echo "Starting SPOT..."

if [[ "${EUID}" -eq 0 ]]; then
    systemctl start "${SERVICE}"
else
    systemctl --user start "${SERVICE}" 2>/dev/null || {
        echo "Error: starting the system SPOT service requires root privileges."
        echo "Try:"
        echo "  sudo ./scripts/start.sh"
        exit 1
    }
fi

echo
echo "SPOT start command completed."
echo

systemctl status "${SERVICE}" --no-pager --lines=10
