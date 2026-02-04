---
name: sb-tracker
description: Simple task tracking for individual agent work. Use when you need to break down a request into sub-tasks, track progress across turns, or maintain a local "todo" list without using the full beads system or git hooks.
---

# SB Tracker (Simple Beads)

A lightweight, standalone task tracker that stores state in a local `.sb.json` file. It's ideal for individual agent sessions to maintain context and track long-running or multi-step tasks.

## Quick Start

- **Initialize**: Run `python3 scripts/sb.py init` if `.sb.json` doesn't exist.
- **Add Task**: `python3 scripts/sb.py add "Task Title" [priority] [desc] [parent_id]`
- **Hierarchy**: Use `parent_id` to create sub-tasks (e.g., `sb-1.1`).
- **List Tasks**: `python3 scripts/sb.py list` (open) or `python3 scripts/sb.py list --all`
- **JSON Output**: Append `--json` to `list` or `show` for machine-readable data.
- **Complete Task**: `python3 scripts/sb.py done sb-1`

## Workflow

1. **Breakdown**: When given a complex task, create `sb-tracker` issues. Use hierarchical IDs for sub-steps (e.g., `add "Sub-step" 2 "..." sb-1`).
2. **Execute**: Work on the highest priority (P0-P1) "ready" task.
3. **Audit**: Use `show <id>` to see the status history and event log.
4. **Context Recovery**: If a session restarts, run `python3 scripts/sb.py list --json` to see the full state.

## Commands

The skill uses `scripts/sb.py`.

### Create and Modify
- **`add`**: `python3 scripts/sb.py add <title> [priority] [desc] [parent_id]`
- **`update`**: `python3 scripts/sb.py update <id> [title=...] [desc=...] [p=...] [parent=...]`
  - Example: `sb update sb-1 p=0 desc="New description"`
- **`dep`**: `python3 scripts/sb.py dep <child> <parent>`

### List and Search
- **`list`**: Shows open tasks with hierarchy.
- **`ready`**: Shows tasks with no open blockers.
- **`search`**: `python3 scripts/sb.py search <keyword>`

### Reporting and Promotion
- **`promote`**: `python3 scripts/sb.py promote <id>`
  - Generates a Markdown summary of the task, its sub-tasks, and its activity log. Use this when you need to report progress to the user or "promote" a private task to a team-wide issue tracker.

### Statistics and Maintenance
- **`stats`**: Overview of progress and priority breakdown.
- **`compact`**: Archive closed tasks to save tokens and context space.

## Agent Operational Loop

To maintain perfect context across sessions, agents should follow this loop:

1. **Onboarding**: At the start of a task, run `sb list --json` or `sb ready` to understand the current state.
2. **Execution**: Focus on the highest priority `ready` tasks.
3. **Updating**: As you complete sub-steps, run `sb done <id>`.
4. **Handoff**: Before ending a session, run `sb stats` to see the remaining work and `sb promote <id>` to provide the user with a clear summary of what was accomplished.
5. **Context Management**: Periodically run `sb compact` if the task list grows beyond ~20 closed items to keep your context window efficient.

### Close Issue
`python3 scripts/sb.py done <id>`
- Moves status to "closed" and sets `closed_at` timestamp.

### Delete Issue
`python3 scripts/sb.py rm <id>`
- Permanently removes the issue from the database.