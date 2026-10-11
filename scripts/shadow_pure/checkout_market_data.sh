#!/usr/bin/env bash
# Sparse, read-only checkout of the market-data branch for the PURE shadow collector.
#
#   scripts/shadow_pure/checkout_market_data.sh <dest> [capture_hours] [projection_days]
#
# Checks out only: the PURE shadow store (data/shadow_pure), the newest Kalshi discovery run, the Kalshi capture
# days and the shadow-v2 V4/V5 projection days the collector reads. Blobless fetch, so only those files download.
set -euo pipefail
DEST="$1"; CAP_HOURS="${2:-3}"; PROJ_DAYS="${3:-3}"
CUT=$(date -u -d "-${CAP_HOURS} hour" +%Y%m%dT%H%M%SZ)
rm -rf "$DEST"
git fetch --no-tags --depth=1 --filter=blob:none origin market-data
git worktree prune
git worktree add --no-checkout -f "$DEST" FETCH_HEAD
cd "$DEST"
git sparse-checkout init --no-cone
LATEST_DISC=$(git ls-tree --name-only HEAD data/kalshi/discovery/ | grep -E '/20[0-9]{6}T[0-9]{6}Z$' | sort | tail -1 || true)
{
  echo "/data/shadow_pure/"
  if [ -n "$LATEST_DISC" ]; then echo "/$LATEST_DISC/markets/KXNFL*.json"; fi
  # quote files of the last CAP_HOURS only (each is ~3-5 MB; a full day is ~370 MB)
  for i in 0 1; do
    D=$(date -u -d "-$i day" +%Y-%m-%d)
    git ls-tree --name-only HEAD "data/kalshi/capture/$D/" | grep '\.quotes\.jsonl$' \
      | awk -F/ -v cut="$CUT" '{ if ($NF >= cut) print "/" $0 }' || true
  done
  # the newest two shadow-v2 V4 / V5 snapshots of the last PROJ_DAYS days (each file is several MB)
  for ARM in DATA_PLAYER_V4 DATA_PLAYER_V5; do
    for i in $(seq 0 "$PROJ_DAYS"); do
      D=$(date -u -d "-$i day" +%Y-%m-%d)
      git ls-tree --name-only HEAD "data/shadow/v2/projections/$D/" | grep "\.$ARM\.projections\.jsonl\.gz$" || true
    done | sort | tail -2 | sed 's#^#/#'
  done
} > .git-sparse-list
git sparse-checkout set --no-cone --stdin < .git-sparse-list
rm -f .git-sparse-list
git checkout -q
echo "market-data checkout at $(git rev-parse --short HEAD): discovery=${LATEST_DISC:-none}"
du -sh data 2>/dev/null || true
