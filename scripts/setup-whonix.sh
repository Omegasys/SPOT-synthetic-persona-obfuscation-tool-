#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WHONIX_CONFIG="${PROJECT_ROOT}/config/network.example.yaml"

echo "========================================"
echo " SPOT WHONIX SETUP"
echo "========================================"
echo

echo "Checking for Whonix/Qubes integration..."

if command -v qvm-check >/dev/null 2>&1; then
    echo "Qubes environment detected."

    echo
    echo "Checking for sys-whonix..."

    if qvm-check sys-whonix >/dev/null 2>&1; then
        echo "FOUND: sys-whonix"
    else
        echo "WARNING: sys-whonix was not found."
        echo "Install/configure Whonix before enabling SPOT networking."
    fi

    echo
    echo "Checking for anon-whonix..."

    if qvm-check anon-whonix >/dev/null 2>&1; then
        echo "FOUND: anon-whonix"
    else
        echo "INFO: anon-whonix was not found."
        echo "SPOT can use another dedicated Whonix workstation."
    fi
else
    echo "Qubes commands were not found."
    echo "Continuing with generic Whonix configuration checks."
fi

echo
echo "Checking SPOT Whonix configuration..."

if [[ -f "${WHONIX_CONFIG}" ]]; then
    echo "FOUND: ${WHONIX_CONFIG}"
else
    echo "WARNING: network.example.yaml was not found."
fi

echo
echo "Recommended SPOT network configuration:"
echo "----------------------------------------"
echo "Mode:                 WHONIX"
echo "Fail closed:          true"
echo "Direct fallback:      false"
echo "DNS bypass:           false"
echo "Kill switch:          enabled"
echo "Network health check: enabled"
echo

echo "Recommended topology:"
echo "  Persona Qube"
echo "       |"
echo "       v"
echo "  Whonix Workstation"
echo "       |"
echo "       v"
echo "  sys-whonix Gateway"
echo "       |"
echo "       v"
echo "      Tor"
echo

echo "Whonix setup preparation complete."
echo
echo "SPOT will not automatically enable a direct-network fallback."
echo "If the Whonix gateway is unavailable, network activity should"
echo "remain blocked."
echo "========================================"
