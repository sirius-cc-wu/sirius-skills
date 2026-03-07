#!/bin/bash
set -e

BRANCH_NAME=$1
COMMIT_MSG=${2:-"docs: add new feature spec"}

if [ -z "$BRANCH_NAME" ]; then
    echo "Usage: $0 <branch_name> [commit_message]"
    exit 1
fi

CURRENT_BRANCH=$(git branch --show-current)

# Ensure there are staged changes
if git diff --cached --quiet; then
    echo "Error: No staged changes found. Please stage your spec/plan first."
    exit 1
fi

echo "Creating branch '$BRANCH_NAME'..."
git checkout -b "$BRANCH_NAME"

echo "Committing staged changes..."
git commit -m "$COMMIT_MSG"

echo "Returning to '$CURRENT_BRANCH'..."
git checkout "$CURRENT_BRANCH"

WORKTREE_PATH="../$BRANCH_NAME"
echo "Creating worktree at '$WORKTREE_PATH'..."
git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"

echo "---------------------------------------------------"
echo "Feature branch '$BRANCH_NAME' created and worktree setup."
echo "Location: $(realpath $WORKTREE_PATH)"
echo "---------------------------------------------------"
