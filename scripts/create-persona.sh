#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
    echo "Usage:"
    echo "  $0 <persona-id> [persona-file]"
    echo
    echo "Examples:"
    echo "  $0 alex"
    echo "  $0 alex examples/alex.yaml"
    exit 1
fi

PERSONA_ID="$1"
PERSONA_FILE="${2:-}"

if [[ ! "${PERSONA_ID}" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "Error: invalid persona ID."
    echo "Use only letters, numbers, '-' and '_'."
    exit 1
fi

echo "Creating SPOT persona: ${PERSONA_ID}"

if [[ -n "${PERSONA_FILE}" ]]; then
    if [[ ! -f "${PERSONA_FILE}" ]]; then
        echo "Error: persona file not found: ${PERSONA_FILE}"
        exit 1
    fi

    echo "Using persona definition:"
    echo "  ${PERSONA_FILE}"

    if command -v spot >/dev/null 2>&1; then
        exec spot persona create \
            --id "${PERSONA_ID}" \
            --file "${PERSONA_FILE}"
    else
        exec python3 -m spot persona create \
            --id "${PERSONA_ID}" \
            --file "${PERSONA_FILE}"
    fi
fi

if command -v spot >/dev/null 2>&1; then
    exec spot persona create --id "${PERSONA_ID}"
else
    exec python3 -m spot persona create --id "${PERSONA_ID}"
fi
