#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
SERVICE_USER="${SPOT_USER:-spot}"
SERVICE_GROUP="${SPOT_GROUP:-spot}"

echo "Installing SPOT..."
echo "Project root: ${PROJECT_ROOT}"

if [[ "${EUID}" -ne 0 ]]; then
    echo "Error: install.sh must be run as root."
    exit 1
fi

if [[ ! -f "${PROJECT_ROOT}/pyproject.toml" ]]; then
    echo "Error: pyproject.toml not found."
    echo "Run this script from a valid SPOT source tree."
    exit 1
fi

if ! command -v "${PYTHON}" >/dev/null 2>&1; then
    echo "Error: ${PYTHON} was not found."
    exit 1
fi

echo "Checking Python..."
"${PYTHON}" --version

echo "Creating service account..."

if ! getent group "${SERVICE_GROUP}" >/dev/null 2>&1; then
    groupadd --system "${SERVICE_GROUP}"
fi

if ! id "${SERVICE_USER}" >/dev/null 2>&1; then
    useradd \
        --system \
        --gid "${SERVICE_GROUP}" \
        --home-dir /var/lib/spot \
        --create-home \
        --shell /usr/sbin/nologin \
        "${SERVICE_USER}"
fi

echo "Creating SPOT directories..."

install -d -o "${SERVICE_USER}" -g "${SERVICE_GROUP}" -m 0750 /var/lib/spot
install -d -o "${SERVICE_USER}" -g "${SERVICE_GROUP}" -m 0750 /var/log/spot
install -d -o "${SERVICE_USER}" -g "${SERVICE_GROUP}" -m 0750 /run/spot
install -d -o "${SERVICE_USER}" -g "${SERVICE_GROUP}" -m 0750 /etc/spot

echo "Installing Python package..."

"${PYTHON}" -m pip install \
    --disable-pip-version-check \
    --no-warn-script-location \
    --upgrade \
    "${PROJECT_ROOT}"

echo "Installing configuration examples..."

if [[ -d "${PROJECT_ROOT}/config" ]]; then
    find "${PROJECT_ROOT}/config" -maxdepth 1 -type f -name '*.yaml' -print0 |
        while IFS= read -r -d '' file; do
            filename="$(basename "${file}")"

            if [[ "${filename}" == *.example.yaml ]]; then
                continue
            fi

            install \
                -o "${SERVICE_USER}" \
                -g "${SERVICE_GROUP}" \
                -m 0640 \
                "${file}" \
                "/etc/spot/${filename}"
        done
fi

echo "Installing systemd units..."

if [[ -d "${PROJECT_ROOT}/systemd" ]]; then
    install -m 0644 \
        "${PROJECT_ROOT}/systemd/spot.service" \
        /etc/systemd/system/spot.service

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
fi

echo "Reloading systemd..."

systemctl daemon-reload

echo "Validating installation..."

if ! "${PYTHON}" -m spot --help >/dev/null 2>&1; then
    echo "Warning: SPOT CLI validation did not succeed."
    echo "The package was installed, but the CLI may not be fully implemented yet."
fi

echo
echo "SPOT installation complete."
echo
echo "Useful commands:"
echo "  systemctl status spot.service"
echo "  systemctl start spot.service"
echo "  systemctl stop spot.service"
echo "  systemctl enable spot.service"
echo
echo "Configuration directory:"
echo "  /etc/spot"
echo
echo "Data directory:"
echo "  /var/lib/spot"
echo
echo "Log directory:"
echo "  /var/log/spot"
