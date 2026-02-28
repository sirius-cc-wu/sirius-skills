#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

npx skills add "$REPO_ROOT/skills/commit"
npx skills add "$REPO_ROOT/skills/sb-tracker"
npx skills add "$REPO_ROOT/skills/simplify"
npx skills add "$REPO_ROOT/skills/batch"
npx skills add https://github.com/google-labs-code/stitch-skills --skill '*'
