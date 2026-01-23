#!/usr/bin/env bash
set -euo pipefail

# Usage: run.sh [worktree-path] [branch-name] [test-command]
WORKTREE_PATH=${1:-}
BRANCH_NAME=${2:-}
TEST_COMMAND=${3:-}

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ -z "$BRANCH_NAME" ]; then
  BRANCH_NAME="${CURRENT_BRANCH}-test"
fi

if [ -z "$WORKTREE_PATH" ]; then
  # sibling directory named <repo-dir>-test
  REPO_BASENAME=$(basename "$REPO_ROOT")
  WORKTREE_PATH="../${REPO_BASENAME}-test"
fi

if [ -d "$WORKTREE_PATH" ]; then
  echo "Using existing worktree at $WORKTREE_PATH"
else
  echo "Creating worktree '$WORKTREE_PATH' with branch '$BRANCH_NAME' from HEAD"
  git worktree add -b "$BRANCH_NAME" "$WORKTREE_PATH" HEAD
fi

cd "$WORKTREE_PATH"

if [ -n "$TEST_COMMAND" ]; then
  echo "Running provided test command: $TEST_COMMAND"
  eval "$TEST_COMMAND"
else
  echo "No test command provided, attempting to detect project type."
  if [ -f "pnpm-lock.yaml" ]; then
    echo "Detected pnpm project. Running 'pnpm install && pnpm test'"
    pnpm install && pnpm test
  elif [ -f "yarn.lock" ]; then
    echo "Detected yarn project. Running 'yarn install && yarn test'"
    yarn install && yarn test
  elif [ -f "package.json" ]; then
    echo "Detected npm project. Running 'npm install && npm test'"
    npm install && npm test
  elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
    echo "Detected Python project. Running 'pytest'"
    pytest
  elif [ -f "go.mod" ]; then
    echo "Detected Go project. Running 'go test ./...'"
    go test ./...
  elif [ -f "Cargo.toml" ]; then
    echo "Detected Rust project. Running 'cargo test'"
    cargo test
  else
    echo "Error: Could not detect project type. Please provide a test command." >&2
    exit 1
  fi
fi
