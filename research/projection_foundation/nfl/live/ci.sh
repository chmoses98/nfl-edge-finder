#!/usr/bin/env bash
# Helpers for .github/workflows/projection-foundation.yml (the `projection-data` archive branch).
#   ci.sh checkout <dir>             clone projection-data (depth 1) into <dir>, or init an empty orphan repo if the branch is missing
#   ci.sh push <dir> "<message>"     commit what changed and push; retries 2/4/8/16 s; archive_guard runs again after a pull
# Only additions are allowed in the immutable directories (pf_core.archive_guard). Never touches any other branch.
set -euo pipefail
BRANCH=projection-data
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PF_ROOT="$(cd "$HERE/../.." && pwd)"
URL="https://x-access-token:${GITHUB_TOKEN:-}@github.com/${GITHUB_REPOSITORY:-chmoses98/nfl-edge-finder}.git"

case "${1:-}" in
  checkout)
    DEST="$2"
    rm -rf "$DEST"
    if git ls-remote --exit-code --heads "$URL" "$BRANCH" >/dev/null 2>&1; then
      git clone --quiet --depth 1 --branch "$BRANCH" "$URL" "$DEST"
      echo "projection-data: checked out $(git -C "$DEST" rev-parse --short HEAD)"
    else
      mkdir -p "$DEST"
      git -C "$DEST" init -q -b "$BRANCH"
      git -C "$DEST" remote add origin "$URL"
      echo "projection-data: branch does not exist yet; starting an orphan archive"
    fi
    ;;
  push)
    DEST="$2"; MSG="$3"
    cd "$DEST"
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add -A
    if git diff --cached --quiet; then echo "projection-data: nothing changed; no commit"; exit 0; fi
    git commit -q -m "$MSG"
    for delay in 0 2 4 8 16; do
      sleep "$delay"
      if git push origin "HEAD:refs/heads/$BRANCH"; then echo "projection-data: pushed $(git rev-parse --short HEAD)"; exit 0; fi
      echo "push failed; fetching the moved branch (merge, no rewrite) and retrying"
      git pull --no-edit --rebase origin "$BRANCH" || { git rebase --abort || true; echo "::error::projection-data diverged and could not be rebased"; exit 1; }
      (cd "$PF_ROOT" && python3 -m pf_core.archive_guard "$DEST")
    done
    echo "::error::projection-data push failed after retries"; exit 1
    ;;
  *) echo "usage: ci.sh checkout <dir> | push <dir> <message>" >&2; exit 2 ;;
esac
