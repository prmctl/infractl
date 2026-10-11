#!/usr/bin/env bash
set -euo pipefail
if [[ ! -d .git ]]; then
  echo 'ERROR: Run this script in the root of your infractl Git repository.' >&2
  exit 1
fi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ ! -f "$SCRIPT_DIR/infractl-release/mkdocs.yml" ]]; then
  echo 'ERROR: Extract the entire ZIP first, keeping the infractl-release directory.' >&2
  exit 1
fi
cp -a "$SCRIPT_DIR/infractl-release/." ./
mkdir -p .github/workflows
for f in .github/workflows/*.yml .github/workflows/*.yaml; do
  [[ -e "$f" ]] || continue
  [[ "$f" == '.github/workflows/pages.yml' ]] || rm -f "$f"
done
printf 'Workflow installed: '; test -f .github/workflows/pages.yml && echo OK
printf 'MkDocs config: '; test -f mkdocs.yml && echo OK
printf 'Docs home: '; test -f docs/index.md && echo OK
git add -A
git status --short
printf '\nReady. Commit and push with:\n  git commit -m "Deploy infractl docs"\n  git push origin master\n'
