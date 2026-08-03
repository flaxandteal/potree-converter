#!/usr/bin/env bash
# ============================================================
#  Potree Converter - drag & drop launcher (macOS / Linux)
#
#  Usage: open a terminal, type this script's path, drag the
#  point-cloud file(s) in after it, and press Enter. On macOS
#  you can also double-click it and pass files when prompted.
#
#  Each input is converted to a Potree octree folder named
#  <file>_potree, placed next to the input.
#
#  Requires Docker Desktop / Docker Engine installed and running.
# ============================================================
set -euo pipefail

IMAGE=ghcr.io/flaxandteal/potree-converter:latest
SCRIPTDIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker not found. Install Docker Desktop and make sure it is running." >&2
  read -r -p "Press Enter to close..."
  exit 1
fi

if [[ $# -eq 0 ]]; then
  echo "Drag point-cloud file(s) into the terminal after this script, e.g.:"
  echo "  \"$0\" cloud.e57 scan.las"
  echo "Supported: .e57 .las .laz .ply .xyz .pcd .pts"
  read -r -p "Press Enter to close..."
  exit 0
fi

# Fetch the image on first use.
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "First run: downloading the converter (a few hundred MB). This only"
  echo "happens once..."
  if ! docker pull "$IMAGE"; then
    echo "Download failed - building it locally instead. This compiles from"
    echo "source and takes several minutes..."
    docker build -t "$IMAGE" "$SCRIPTDIR"
  fi
fi

for f in "$@"; do
  if [[ ! -f "$f" ]]; then
    echo "*** Skipping (not a file): $f"
    continue
  fi
  indir="$(cd "$(dirname "$f")" && pwd)"
  fname="$(basename "$f")"
  base="${fname%.*}"
  echo
  echo "=== Converting $fname ==="
  docker run --rm --user "$(id -u):$(id -g)" \
    -v "$indir:/data" "$IMAGE" "/data/$fname" -o "/data/${base}_potree"
  echo "Done: $indir/${base}_potree"
done

echo
read -r -p "All conversions finished. Press Enter to close..."
