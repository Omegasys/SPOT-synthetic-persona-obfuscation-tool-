#!/usr/bin/env bash
set -euo pipefail

SERVICE_USER="${SPOT_USER:-spot}"
SERVICE_GROUP="${SPOT_GROUP:-spot}"

REMOVE_DATA="${REMOVE_DATA:-false}"
REMOVE_CONFIG="${REMOVE_CONFIG:-false}"
REMOVE_LOGS="${REMOVE_LOGS:-false}"

echo "Uninstalling SPOT..."

if [[ "${EUID}" -ne 0 ]]; then
    echo "Error: uninstall.sh must be run as root."
    exit 1
fi

echo
echo "This will remove the SPOT software and system service."
echo "User data is preserved by default."
echo

systemctl stop spot.service 2>/dev/null || true
systemctl stop spot.timer 2>/dev/null || true
systemctl stop spot-emergency.service 2>/dev/null || true

systemctl disable spot.service 2>/dev/null || true
systemctl disable spot.timer 2>/dev/null || true
systemctl disable spot-emergency.service 2>/dev/null || true

echo "Removing systemd units..."

rm -f /etc/systemd/system/spot.service
rm -f /etc/systemd/system/spot.timer
rm -f /etc/systemd/system/spot-emergency.service

systemctl daemon-reload
systemctl reset-failed 2>/dev/null || true

echo "Removing installed Python package..."

python3 -m pip uninstall -y spot 2>/dev/null || true

if [[ "${REMOVE_CONFIG}" == "true" ]]; then
    echo "Removing configuration..."
    rm -rf /etc/spot
else
    echo "Preserving configuration: /etc/spot"
fi

if [[ "${REMOVE_LOGS}" == "true" ]]; then
    echo "Removing logs..."
    rm -rf /var/log/spot
else
    echo "Preserving logs: /var/log/spot"
fi

if [[ "${REMOVE_DATA}" == "true" ]]; then
    echo "Removing SPOT data..."
    rm -rf /var/lib/spot
else
    echo "Preserving data: /var/lib/spot"
fi

rm -rf /run/spot

echo "Removing service account..."

if id "${SERVICE_USER}" >/dev/null 2>&1; then
    userdel "${SERVICE_USER}" 2>/dev/null || true
fi

if getent group "${SERVICE_GROUP}" >/dev/null 2>&1; then
    groupdel "${SERVICE_GROUP}" 2>/dev/null || true
fi

echo
echo "SPOT software has been uninstalled."

if [[ "${REMOVE_DATA}" != "true" ]]; then
    echo "SPOT data was preserved in /var/lib/spot."
fi

if [[ "${REMOVE_CONFIG}" != "true" ]]; then
    echo "SPOT configuration was preserved in /etc/spot."
fi

if [[ "${REMOVE_LOGS}" != "true" ]]; then
    echo "SPOT logs were preserved in /var/log/spot."
fi
