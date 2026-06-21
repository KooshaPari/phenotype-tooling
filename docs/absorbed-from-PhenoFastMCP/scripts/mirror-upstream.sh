#!/usr/bin/env bash
# Supplemental sync: push upstream heads+tags into an EXISTING GitHub fork.
#
# PREREQUISITE: KooshaPari/PhenoFastMCP must already be a GitHub fork of
# PrefectHQ/fastmcp (gh repo fork). Do NOT use this to bootstrap from an empty
# repo — that breaks fork: true / parent tracking.
#
# Does NOT push refs/pull/* (GitHub rejects hidden refs on forks).
set -euo pipefail

UPSTREAM="${UPSTREAM:-https://github.com/PrefectHQ/fastmcp.git}"
FORK="${FORK:-https://github.com/KooshaPari/PhenoFastMCP.git}"
WORKDIR="${WORKDIR:-/tmp/fastmcp-mirror.git}"

rm -rf "$WORKDIR"
git clone --mirror "$UPSTREAM" "$WORKDIR"
cd "$WORKDIR"

git remote set-url origin "$FORK"
git config remote.origin.mirror false

echo "Pushing $(git for-each-ref --format='%(refname:short)' refs/heads/ | wc -l) branches..."
git push origin 'refs/heads/*:refs/heads/*'

echo "Pushing $(git for-each-ref --format='%(refname:short)' refs/tags/ | wc -l) tags..."
git push origin 'refs/tags/*:refs/tags/*'

echo "Pull refs preserved locally only:"
git for-each-ref --format='%(refname)' refs/pull/ | wc -l
