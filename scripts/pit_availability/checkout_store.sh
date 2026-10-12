#!/usr/bin/env bash
# Sparse, read-only checkout of the published PIT availability store (data/pit_availability) from market-data.
#   scripts/pit_availability/checkout_store.sh <dest>
set -euo pipefail
DEST="$1"
rm -rf "$DEST"
git fetch --no-tags --depth=1 --filter=blob:none origin market-data
git worktree prune
git worktree add --no-checkout -f "$DEST" FETCH_HEAD
cd "$DEST"
git sparse-checkout init --no-cone
echo "/data/pit_availability/" | git sparse-checkout set --no-cone --stdin
git checkout -q
echo "market-data checkout at $(git rev-parse --short HEAD)"
