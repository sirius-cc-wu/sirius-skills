---
name: create-worktree-and-test
description: Create a new git worktree from current branch and run tests.
---

# Create Worktree & Run Tests

Provides a script that creates a new git worktree from the
current branch (HEAD) and runs tests inside the new worktree.

## Usage

Run: `<path-to-skill>/scripts/run.sh [worktree-path] [branch-name] [test-command]`

- If `worktree-path` is omitted the script creates a sibling directory named `<repo-root>-test`.
- If `branch-name` is omitted the script uses `<current-branch>-test`.
- If `test-command` is omitted, the script attempts to detect the project type and run a default test command (e.g., `npm test`, `pytest`).

## Requirements

- `git` available in PATH

## Behavior

- If the target worktree directory already exists, the script will use it.
- Otherwise, the script creates a new branch from `HEAD` and adds a worktree at the requested path.
- The script will then change into the worktree directory and execute the test command.
