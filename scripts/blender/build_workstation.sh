#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
workdir="${WORKSTATION_WORKDIR:-/tmp/adoreblvnk-workstation-build}"
target="${WORKSTATION_TARGET:-$root/public/models/workstation-world.glb}"
raw="$workdir/workstation-world.raw.glb"
compressed="$workdir/workstation-world.glb"
log="$workdir/blender.log"

mkdir -p "$workdir" "$(dirname "$target")"
rm -f "$raw" "$compressed" "$target.tmp"

WORKSTATION_OUT="$raw" \
WORKSTATION_WORKDIR="$workdir" \
WORKSTATION_SKIP_DIAGNOSTICS="${WORKSTATION_SKIP_DIAGNOSTICS:-0}" \
blender --background --python "$root/scripts/blender/create_workstation_world.py" 2>&1 | tee "$log"

test -s "$raw"
if grep -q 'Traceback (most recent call last)' "$log"; then
  echo 'Blender reported a Python traceback.' >&2
  exit 1
fi

npx --yes @gltf-transform/cli@4.4.2 meshopt "$raw" "$compressed"
test -s "$compressed"
install -m 0644 "$compressed" "$target.tmp"
mv "$target.tmp" "$target"

sha256sum "$target"
stat -c 'bytes=%s' "$target"
