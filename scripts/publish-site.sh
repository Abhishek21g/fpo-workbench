#!/usr/bin/env bash
# Sync site/ to enaguthi.com — ONLY touches fpo-workbench/ on gh-pages (safe alongside other projects).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${SITE_REPO:-$HOME/Documents/Abhishek21g.github.io}"
TARGET="fpo-workbench"

if [[ ! -d "$DEST/.git" ]]; then
  echo "error: main site repo not found at $DEST" >&2
  echo "Clone: git clone git@github.com:Abhishek21g/Abhishek21g.github.io.git $DEST" >&2
  exit 1
fi

echo "==> Refresh demo data"
"$ROOT/scripts/export_site_data.sh"

echo "==> Publish to $DEST/$TARGET/ (gh-pages branch only)"
cd "$DEST"

# Remember current branch to restore if publish fails mid-way
PREV_BRANCH="$(git branch --show-current 2>/dev/null || echo main)"

cleanup() {
  git checkout "$PREV_BRANCH" 2>/dev/null || true
}
trap cleanup EXIT

git fetch origin gh-pages
git checkout gh-pages
git pull origin gh-pages --no-rebase

mkdir -p "$TARGET"
# Scoped sync — does NOT touch hexo-sia-eval, ramp-agent-kit, etc.
rsync -av --delete "$ROOT/site/" "$DEST/$TARGET/site/"
cp "$ROOT/index.html" "$DEST/$TARGET/index.html"

git add "$TARGET/"
if git diff --cached --quiet; then
  echo "No site changes to publish."
  exit 0
fi

git commit -m "Sync FPO++ Training Workbench site from fpo-workbench"
git pull origin gh-pages --no-rebase
git push origin gh-pages

trap - EXIT
git checkout "$PREV_BRANCH" 2>/dev/null || git checkout main 2>/dev/null || true

echo "Published: https://enaguthi.com/fpo-workbench/site/"
echo "Tip: hard-refresh (Cmd+Shift+R) if styles look stale."
