#!/usr/bin/env bash
# Sync site/ to enaguthi.com via Abhishek21g.github.io public/ on MAIN (not gh-pages).
#
# enaguthi.com deploys from main → npm run build → out/ → gh-pages (clean: true).
# Direct gh-pages pushes are wiped on the next main deploy. See portfolio-deploy.mdc.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${SITE_REPO:-$HOME/Documents/Abhishek21g.github.io}"
TARGET="public/fpo-workbench"

if [[ ! -d "$DEST/.git" ]]; then
  echo "error: portfolio repo not found at $DEST" >&2
  echo "Clone: git clone git@github.com:Abhishek21g/Abhishek21g.github.io.git $DEST" >&2
  exit 1
fi

echo "==> Refresh demo data"
"$ROOT/scripts/export_site_data.sh"

echo "==> Sync to $DEST/$TARGET/ (main branch)"
cd "$DEST"
PREV_BRANCH="$(git branch --show-current 2>/dev/null || echo main)"
trap 'git checkout "$PREV_BRANCH" 2>/dev/null || true' EXIT

git checkout main
git pull origin main --no-rebase

mkdir -p "$TARGET"
rsync -av --delete "$ROOT/site/" "$DEST/$TARGET/site/"
cp "$ROOT/index.html" "$DEST/$TARGET/index.html"

git add "$TARGET/"
if git diff --cached --quiet; then
  echo "No site changes to publish."
  exit 0
fi

git commit -m "Add FPO++ Training Workbench demo to public/fpo-workbench"
git pull origin main --no-rebase
git push origin main

trap - EXIT

echo "Published to main — GitHub Actions will deploy to https://enaguthi.com/fpo-workbench/site/"
echo "Monitor: https://github.com/Abhishek21g/Abhishek21g.github.io/actions"
echo "Tip: hard-refresh (Cmd+Shift+R) after deploy completes (~2 min)."
