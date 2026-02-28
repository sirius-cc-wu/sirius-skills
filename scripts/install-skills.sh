#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMMON_FLAGS=(
  --global
  --yes
  --agent github-copilot
  --agent codex
  --agent antigravity
  --agent gemini-cli
)

npx skills add "$REPO_ROOT/skills/commit" "${COMMON_FLAGS[@]}"
npx skills add "$REPO_ROOT/skills/sb-tracker" "${COMMON_FLAGS[@]}"
npx skills add "$REPO_ROOT/skills/simplify" "${COMMON_FLAGS[@]}"
npx skills add "$REPO_ROOT/skills/batch" "${COMMON_FLAGS[@]}"
npx skills add https://github.com/google-labs-code/stitch-skills --skill '*' "${COMMON_FLAGS[@]}"
