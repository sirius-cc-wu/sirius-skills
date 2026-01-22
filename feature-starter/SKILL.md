---
name: feature-starter
description: Automates the process of starting a new feature by committing staged changes (specs) to a new branch and creating a separate worktree.
---

# Feature Starter Skill

This skill helps you initialize a new feature development environment properly.

## When to Use

Use this skill when you have:
1.  Created a new spec or plan file.
2.  Staged those files.
3.  Want to implement the feature in a clean, isolated worktree without disturbing your current workspace.

## Workflow

The skill provides a script to automate the git gymnastics required to move staged changes to a new branch and open a worktree.

### 1. Identify Branch Name
Determine the branch name from your spec file (e.g., `007-refactor-uds-file-transfer-server`).

### 2. Run the Start Script
Execute the bundled script to create the branch, commit changes, and setup the worktree.

```bash
bash .github/skills/feature-starter/scripts/start_feature.sh <branch-name> "<commit-message>"
```

**Example:**
```bash
bash .github/skills/feature-starter/scripts/start_feature.sh 007-refactor-uds-file-transfer-server "docs: add spec for uds file transfer refactor"
```

### 3. Open the Worktree
After the script completes, open the new worktree directory in your editor (or a new window).
The script will output the path, usually `../<branch-name>`.

## Manual Steps (Reference)

If the script fails or you prefer manual control:

1.  Create and switch to new branch: `git checkout -b my-feature`
2.  Commit staged changes: `git commit -m "docs: add spec"`
3.  Return to main branch: `git checkout master`
4.  Create worktree: `git worktree add ../my-feature my-feature`
