---
name: specify
description: Deprecated compatibility alias for `define`.
---

# Specify

This skill has been renamed to `define`.

Use `define` as the canonical execution-layer skill for creating task-scoped `brief.md` files.

If you still invoke `specify`, follow the same behavior and outputs as `define`:

- create or update `<track_path>/brief.md`
- create or update `<track_path>/checklists/requirements.md`
- use the templates and rules in `skills/define/`

When updating docs or workflow examples, prefer `define` over `specify`.
