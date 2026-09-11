#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SYSTEMD_DIR="${PROJECT_ROOT}/systemd"

echo "========================================"
echo " SPOT SYSTEMD SETUP"
echo "========================================"
echo

if [[ "${EUID}" -ne 0 ]]; then
    echo "Error: setup-systemd.sh must be run as root."
    echo
    echo "Try:"
    echo "  sudo ./scripts/setup-systemd.sh"
    exit 1
fi

if [[ ! -d "${SYSTEMD_DIR}" ]]; then
    echo "Error: systemd directory not found:"
    echo "  ${SYSTEMD_DIR}"
    exit 1
fi

echo "Installing systemd units..."

if [[ -f "${SYSTEMD_DIR}/spot.service" ]]; then
    install -m 0644 \
        "${SYSTEMD_DIR}/spot.service" \
        /etc/systemd/system/spot.service
    echo "Installed spot.service"
fi

if [[ -f "${SYSTEMD_DIR}/spot.timer" ]]; then
    install -m 0644 \
        "${SYSTEMD_DIR}/spot.timer" \
        /etc/systemd/system/spot.timer
    echo "Installed spot.timer"
fi

if [[ -f "${SYSTEMD_DIR}/spot-emergency.service" ]]; then
    install -m 0644 \
        "${SYSTEMD_DIR}/spot-emergency.service" \
        /etc/systemd/system/spot-emergency.service
    echo "Installed spot-emergency.service"
fi

echo
echo "Reloading systemd..."

systemctl daemon-reload

echo
echo "Checking installed units..."

systemctl cat spot.service >/dev/null 2>&1 && \
    echo "spot.service: OK"

systemctl cat spot.timer >/dev/null 2>&1 && \
    echo "spot.timer: OK"

systemctl cat spot-emergency.service >/dev/null 2>&1 && \
    echo "spot-emergency.service: OK"

echo
echo "SPOT systemd setup complete."
echo
echo "The service has NOT been automatically enabled or started."
echo
echo "To start manually:"
echo "  systemctl start spot.service"
echo
echo "To enable at boot:"
echo "  systemctl enable spot.service"
echo
echo "To enable the timer:"
echo "  systemctl enable --now spot.timer"
echo
echo "To perform an emergency stop:"
echo "  ./scripts/emergency-stop.sh"
echo "========================================"
