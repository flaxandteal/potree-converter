#!/usr/bin/env bash
# Entry point: transparently converts non-LAS/LAZ inputs (e57, ply, xyz, ...)
# to .laz via PDAL, then hands the cloud to PotreeConverter 2.1.1.
#
# Usage is identical to PotreeConverter, e.g.:
#   docker run --rm -v $PWD:/data img INPUT.e57 -o OUTDIR
set -euo pipefail

POTREE=/src/PotreeConverter/build/PotreeConverter
PDAL=pdal
# PotreeConverter's own libs, plus the conda base libs (TBB, libstdc++, ...).
POTREE_LIBS=/src/PotreeConverter/build:/src/PotreeConverter/build/Converter/libs/laszip:/opt/conda/lib

args=("$@")
input_idx=-1
input=""

# Find the first argument that is an existing point-cloud file.
for i in "${!args[@]}"; do
  a="${args[$i]}"
  case "${a,,}" in
    *.las|*.laz|*.e57|*.ply|*.xyz|*.pcd|*.pts|*.bpf)
      if [[ -f "$a" ]]; then input="$a"; input_idx=$i; break; fi
      ;;
  esac
done

if [[ -n "$input" ]]; then
  case "${input,,}" in
    *.las|*.laz)
      : ;;  # native PotreeConverter input — nothing to do
    *)
      converted="/tmp/$(basename "${input%.*}").laz"
      echo ">> $input is not LAS/LAZ — converting to $converted via PDAL" >&2
      # Run pdal with a clean LD_LIBRARY_PATH so it uses its own conda libs.
      env -u LD_LIBRARY_PATH "$PDAL" translate "$input" "$converted"
      args[$input_idx]="$converted"
      ;;
  esac
fi

export LD_LIBRARY_PATH="$POTREE_LIBS"
exec "$POTREE" "${args[@]}"
