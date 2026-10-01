#!/usr/bin/env bash
# Move an EXISTING market-data worktree to the branch's newest tip IN PLACE, and drop the publisher's scratch
# checkout.
#
#   scripts/ci/refresh_market_data_worktree.sh /tmp/md
#
# Why this exists. A job that publishes and then rebuilds a report from what it just published needs the newer
# tip. postgame-settle.yml used to get it with `git worktree add` of a FRESH full checkout per report (/tmp/md2,
# /tmp/md3), on top of /tmp/md and the publisher's own full checkout (../_market_data_wt). With the corpus at
# several GB that is four full copies of market-data on one runner, and on 2026-09-27/28/29 the runner died a
# few seconds into creating the fourth -- three runs, logs unrecoverable, the three-arm report never rebuilt,
# and Week 3's player autopsy read as 69 projections (ATL-GB alone) while 1,012 sat in the corpus. Every run
# that skipped the incumbent report (no /tmp/md2) rebuilt the three-arm report fine.
#
# A checkout of a newer commit rewrites only the files that changed, so this costs the delta, not a copy.
set -euo pipefail
wt="${1:?usage: refresh_market_data_worktree.sh <existing market-data worktree>}"
git fetch --depth=1 origin market-data
git -C "$wt" checkout -q -f --detach origin/market-data
# publish_market_data.py recreates this on every publish; between publishes it is a dead full checkout.
scratch="$(dirname "$(git rev-parse --show-toplevel)")/_market_data_wt"
if [ -d "$scratch" ]; then rm -rf "$scratch"; git worktree prune; fi
git -C "$wt" log -1 --format='market-data now at %h (%cI)'
