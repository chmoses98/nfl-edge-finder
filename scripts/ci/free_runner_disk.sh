#!/usr/bin/env bash
# Make room on a GitHub-hosted runner for the market-data worktree.
#
# `git fetch --depth=1 origin market-data` + `git worktree add` now needs ~52 GB (2026-10-07: 12 GB of packs,
# 39.8 GB of tree, growing ~1 GB a day with captures and shadow-v2 projections). From 2026-10-06 06:09Z jobs that
# take that worktree died with "No space left on device" (runner annotations on shadow-price 37425883411 and
# 37487350972, shadow-v2-project, shadow-v2-settle): the runner lost its own log, the step stayed "in progress"
# and nothing after it -- ledger, report, app export -- ran. This removes preinstalled toolchains none of these
# jobs use (Android SDK, .NET, Haskell, CodeQL, Swift, Boost, PowerShell, cached Docker images), ~25-30 GB.
# The Python toolcache that actions/setup-python uses is NOT touched. Never fails the job: it only frees space.
set -u
echo "disk before:"; df -h / /mnt 2>/dev/null || df -h /
for d in /usr/local/lib/android /usr/share/dotnet /opt/ghc /usr/local/.ghcup /opt/hostedtoolcache/CodeQL \
         /usr/share/swift /usr/local/share/boost /usr/local/share/powershell /opt/microsoft; do
  [ -e "$d" ] && sudo rm -rf "$d"
done
sudo docker image prune --all --force >/dev/null 2>&1 || true
echo "disk after:"; df -h / /mnt 2>/dev/null || df -h /
exit 0
