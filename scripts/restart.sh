#!/usr/bin/env bash
set -euo pipefail

SERVICE="spot.service"

echo "Restarting SPOT..."

if [[ "${EUID}" -eq 0 ]]; then
    systemctl restart "${SERVICE}"
else
    systemctl --user restart "${SERVICE}" 2>/dev/null || {
        echo "Error: restarting the system SPOT service requires root privileges."
        echo "Try:"
        echo "  sudo ./scripts/restart.sh"
        exit 1
    }
fi

echo
echo "SPOT restart command completed."
echo

systemctl status "${SERVICE}" --no-pager --lines=10
