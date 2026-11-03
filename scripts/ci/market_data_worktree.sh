#!/usr/bin/env bash
# Check out the market-data worktree on the filesystem with the most free space, and expose it at /tmp/md.
#
# Why: `git worktree add` of market-data is a ~52 GB tree (scripts/ci/free_runner_disk.sh). A GitHub-hosted runner's
# root filesystem cannot hold it even after the preinstalled toolchains are removed (that frees ~25-30 GB on top of
# what is already free); the runner's second disk (/mnt) is much larger. shadow-v2-settle died inside its fetch step
# with "No space left on device" (run 41513363507). Every driver reads `--market-data /tmp/md`, so the tree is placed
# on the big disk and /tmp/md is a symlink to it: no driver path changes. git resolves the symlink and registers the
# real path, so the worktree is an ordinary one.
#
# Run AFTER `git fetch --depth=1 origin market-data`. Fails closed with a clear message when no candidate filesystem
# has MD_MIN_FREE_GB free, instead of filling a disk half-way and losing the runner's log (what "No space left on
# device" did before).
#
# Environment (all optional; the defaults are the runner layout):
#   MD_LINK          path the drivers read                       (/tmp/md)
#   MD_CANDIDATES    space-separated directories to consider      (/mnt /tmp)
#   MD_SUBDIR        directory created under the chosen candidate (md-worktree)
#   MD_REF           ref to check out                             (origin/market-data)
#   MD_MIN_FREE_GB   free space required on the chosen filesystem (60)  -- an owner-adjustable policy value
set -euo pipefail

LINK="${MD_LINK:-/tmp/md}"
CANDIDATES="${MD_CANDIDATES:-/mnt /tmp}"
SUBDIR="${MD_SUBDIR:-md-worktree}"
REF="${MD_REF:-origin/market-data}"
MIN_FREE_GB="${MD_MIN_FREE_GB:-60}"

best=""
best_kb=-1
for dir in $CANDIDATES; do
  [ -d "$dir" ] || continue
  kb="$(df -Pk "$dir" | awk 'NR==2 {print $4}')"
  [ -n "$kb" ] || continue
  echo "candidate $dir: $((kb / 1024 / 1024)) GB free"
  if [ "$kb" -gt "$best_kb" ]; then best="$dir"; best_kb="$kb"; fi
done

if [ -z "$best" ]; then
  echo "::error::no candidate directory exists among: $CANDIDATES" >&2
  exit 2
fi
best_gb=$((best_kb / 1024 / 1024))
if [ "$best_gb" -lt "$MIN_FREE_GB" ]; then
  echo "::error::the market-data worktree needs about $MIN_FREE_GB GB; the largest free filesystem ($best) has $best_gb GB. Refusing to start a checkout that would exhaust the disk." >&2
  exit 3
fi

target="$best/$SUBDIR"
if ! mkdir -p "$target" 2>/dev/null; then
  sudo mkdir -p "$target"
  sudo chown "$(id -u):$(id -g)" "$target"
fi
# a previous worktree registration for this path (a re-run on a reused checkout) must not block the add
git worktree prune
rm -rf "$LINK"
rm -rf "$target"/* "$target"/.[!.]* 2>/dev/null || true
ln -sfn "$target" "$LINK"

git worktree add -f "$LINK" "$REF"
echo "market-data worktree: $target (linked at $LINK), $best_gb GB were free"
df -h "$best" | tail -n 1
