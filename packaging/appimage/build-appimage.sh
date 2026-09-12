#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
PACKAGING_DIR="${PROJECT_ROOT}/packaging/appimage"

VERSION="$(sed -n 's/^VERSION *= *"\([^"]*\)".*/\1/p' \
    "${PROJECT_ROOT}/src/spot/version.py" | head -n 1)"

if [[ -z "${VERSION}" ]]; then
    echo "Unable to determine SPOT version." >&2
    exit 1
fi

ARCH="$(uname -m)"

case "${ARCH}" in
    x86_64)
        APPIMAGE_ARCH="x86_64"
        ;;
    aarch64|arm64)
        APPIMAGE_ARCH="aarch64"
        ;;
    *)
        echo "Unsupported architecture: ${ARCH}" >&2
        exit 1
        ;;
esac

if ! command -v appimagetool >/dev/null 2>&1; then
    echo "appimagetool is required to build the AppImage." >&2
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required." >&2
    exit 1
fi

BUILD_ROOT="${PROJECT_ROOT}/build/appimage"
APPDIR="${BUILD_ROOT}/SPOT.AppDir"
DIST_DIR="${PROJECT_ROOT}/dist"

rm -rf "${APPDIR}"
mkdir -p \
    "${APPDIR}/usr/bin" \
    "${APPDIR}/usr/lib" \
    "${APPDIR}/usr/share/applications" \
    "${APPDIR}/usr/share/icons/hicolor/scalable/apps" \
    "${APPDIR}/usr/share/spot"

# Copy the application source.
mkdir -p "${APPDIR}/usr/lib/python3/site-packages"
cp -a "${PROJECT_ROOT}/src/spot" \
    "${APPDIR}/usr/lib/python3/site-packages/"

# Copy configuration examples when present.
if [[ -d "${PROJECT_ROOT}/config" ]]; then
    cp -a "${PROJECT_ROOT}/config" \
        "${APPDIR}/usr/share/spot/"
fi

# Copy reusable synthetic personality templates.
if [[ -d "${PROJECT_ROOT}/personalities" ]]; then
    cp -a "${PROJECT_ROOT}/personalities" \
        "${APPDIR}/usr/share/spot/"
fi

# Copy examples.
if [[ -d "${PROJECT_ROOT}/examples" ]]; then
    cp -a "${PROJECT_ROOT}/examples" \
        "${APPDIR}/usr/share/spot/"
fi

install -Dm0755 \
    "${PACKAGING_DIR}/AppRun" \
    "${APPDIR}/AppRun"

install -Dm0644 \
    "${PACKAGING_DIR}/spot.desktop" \
    "${APPDIR}/usr/share/applications/spot.desktop"

install -Dm0644 \
    "${PACKAGING_DIR}/spot.svg" \
    "${APPDIR}/spot.svg"

install -Dm0644 \
    "${PACKAGING_DIR}/spot.svg" \
    "${APPDIR}/usr/share/icons/hicolor/scalable/apps/spot.svg"

mkdir -p "${DIST_DIR}"

OUTPUT="${DIST_DIR}/SPOT-${VERSION}-${APPIMAGE_ARCH}.AppImage"

rm -f "${OUTPUT}"

ARCH="${APPIMAGE_ARCH}" \
    appimagetool \
    "${APPDIR}" \
    "${OUTPUT}"

chmod 0755 "${OUTPUT}"

echo
echo "AppImage created:"
echo "${OUTPUT}"
