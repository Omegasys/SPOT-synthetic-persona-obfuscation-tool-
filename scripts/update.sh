#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"

echo "Updating SPOT..."

if [[ "${EUID}" -ne 0 ]]; then
    echo "Error: update.sh must be run as root."
    exit 1
fi

if [[ ! -f "${PROJECT_ROOT}/pyproject.toml" ]]; then
    echo "Error: pyproject.toml not found."
    echo "Run this script from a valid SPOT source tree."
    exit 1
fi

echo "Project root: ${PROJECT_ROOT}"

echo "Stopping SPOT..."

systemctl stop spot.service 2>/dev/null || true

echo "Updating Python package..."

"${PYTHON}" -m pip install \
    --disable-pip-version-check \
    --no-warn-script-location \
    --upgrade \
    "${PROJECT_ROOT}"

echo "Updating systemd units..."

if [[ -f "${PROJECT_ROOT}/systemd/spot.service" ]]; then
    install -m 0644 \
        "${PROJECT_ROOT}/systemd/spot.service" \
        /etc/systemd/system/spot.service
fi

if [[ -f "${PROJECT_ROOT}/systemd/spot.timer" ]]; then
    install -m 0644 \
        "${PROJECT_ROOT}/systemd/spot.timer" \
        /etc/systemd/system/spot.timer
fi

if [[ -f "${PROJECT_ROOT}/systemd/spot-emergency.service" ]]; then
    install -m 0644 \
        "${PROJECT_ROOT}/systemd/spot-emergency.service" \
        /etc/systemd/system/spot-emergency.service
fi

systemctl daemon-reload

echo "Validating SPOT..."

"${PYTHON}" -m spot --help >/dev/null 2>&1 || {
    echo "Warning: SPOT CLI validation failed."
}

echo
echo "SPOT update complete."
echo "Existing data and configuration were not intentionally removed."
echo
echo "Start SPOT with:"
echo "  ./scripts/start.sh"
