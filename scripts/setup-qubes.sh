#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUBES_DIR="${PROJECT_ROOT}/qubes"

echo "========================================"
echo " SPOT QUBES SETUP"
echo "========================================"
echo

if [[ ! -d "${QUBES_DIR}" ]]; then
    echo "Error: Qubes integration directory not found:"
    echo "  ${QUBES_DIR}"
    exit 1
fi

if ! command -v qvm-check >/dev/null 2>&1; then
    echo "Error: qvm-check was not found."
    echo "This script must be run inside a Qubes OS environment."
    exit 1
fi

echo "Qubes environment detected."

echo
echo "SPOT Qubes components:"
echo "----------------------------------------"

for path in \
    "${QUBES_DIR}/README.md" \
    "${QUBES_DIR}/templates/spot-persona-template.xml" \
    "${QUBES_DIR}/templates/spot-disposable-template.xml" \
    "${QUBES_DIR}/services/spot-controller" \
    "${QUBES_DIR}/services/spot-persona" \
    "${QUBES_DIR}/services/spot-network" \
    "${QUBES_DIR}/policies/spot.policy" \
    "${QUBES_DIR}/policies/spot-firewall.policy"
do
    if [[ -f "${path}" ]]; then
        echo "FOUND  ${path#${PROJECT_ROOT}/}"
    else
        echo "MISSING ${path#${PROJECT_ROOT}/}"
    fi
done

echo
echo "Checking required Qubes commands..."

for command in qvm-create qvm-start qvm-shutdown qvm-ls qvm-check; do
    if command -v "${command}" >/dev/null 2>&1; then
        echo "FOUND  ${command}"
    else
        echo "MISSING ${command}"
    fi
done

echo
echo "Checking SPOT policy files..."

if [[ -f "${QUBES_DIR}/policies/spot.policy" ]]; then
    echo "SPOT RPC policy is present."
fi

if [[ -f "${QUBES_DIR}/policies/spot-firewall.policy" ]]; then
    echo "SPOT firewall policy is present."
fi

echo
echo "Qubes setup preparation complete."
echo
echo "IMPORTANT:"
echo "The files in qubes/templates/ are SPOT metadata/templates,"
echo "not blindly importable native Qubes template definitions."
echo
echo "Review and adapt the policy files to the installed Qubes OS"
echo "release before enabling them."
echo
echo "Recommended topology:"
echo "  SPOT Persona Qube"
echo "        |"
echo "        v"
echo "  SPOT Network Boundary"
echo "        |"
echo "        v"
echo "  sys-whonix"
echo "        |"
echo "        v"
echo "       Tor"
echo
echo "No unrestricted dom0 access should be granted."
echo "========================================"
