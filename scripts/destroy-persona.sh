#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage:"
    echo "  $0 <persona-id>"
    exit 1
fi

PERSONA_ID="$1"

if [[ ! "${PERSONA_ID}" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "Error: invalid persona ID."
    exit 1
fi

echo "Destroying SPOT persona: ${PERSONA_ID}"
echo
echo "WARNING: This may remove the persona's isolated state."
echo

read -r -p "Type the persona ID to confirm: " CONFIRMATION

if [[ "${CONFIRMATION}" != "${PERSONA_ID}" ]]; then
    echo "Confirmation did not match."
    echo "No changes were made."
    exit 1
fi

echo
echo "Stopping persona..."

if command -v spot >/dev/null 2>&1; then
    spot persona stop --id "${PERSONA_ID}" 2>/dev/null || true
else
    python3 -m spot persona stop --id "${PERSONA_ID}" 2>/dev/null || true
fi

echo "Destroying persona..."

if command -v spot >/dev/null 2>&1; then
    exec spot persona destroy --id "${PERSONA_ID}"
else
    exec python3 -m spot persona destroy --id "${PERSONA_ID}"
fi
