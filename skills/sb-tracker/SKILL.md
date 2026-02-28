---
name: sb-tracker
description: Track work with the `sb` CLI by creating, updating, listing, and completing tasks with priorities, dependencies, and repo/global filters. Use for any coding agent that needs a lightweight task tracker for long-running or multi-step work, context recovery across sessions, or end-of-session handoff.
---

# SB Tracker

Use `sb` to maintain a lightweight task list in a global JSON DB (default `~/.sb.json`).

## Install

Verify the CLI is present:

```bash
sb --help
```

## Core Workflow

1. Initialize the DB once with `sb init` (global by default).
2. Add tasks with priorities and optional descriptions or parents.
3. Work the highest-priority ready task.
4. Mark tasks done as you complete them.
5. At session end, list all tasks and summarize status.

## Key Commands

```bash
sb init
sb add "Task Title" [priority] [desc] [parent_id]
sb list
sb list --all
sb list --repo
sb list --global
sb ready
sb show <id> [--json]
sb search <keyword> [--repo|--global]
sb update <id> [title=...] [desc=...] [p=...] [parent=...]
sb dep <child> <parent> [--repo|--global]
sb done <id>
sb rm <id>
sb stats
sb compact
```

## Priority Scale

Use numeric priorities when adding or updating:

```bash
0 = P0 Critical
1 = P1 High
2 = P2 Medium (default)
3 = P3 Low
```

Example:

```bash
sb add "Fix critical bug" 0 "Blocks release"
```

## Session Completion Checklist

1. File remaining work as tasks or subtasks.
2. Verify results (tests, screenshots, etc.).
3. Mark completed tasks with `sb done <id>`.
4. Optionally run `sb compact` to prune closed tasks.
5. List all tasks with `sb list --all`.
6. Provide a brief handoff summary and the next task to pick up.

## Notes

- Override DB path with `SB_DB_PATH=/path/to/db.json` when needed.
- Use `sb list --json` for context recovery on restart.
