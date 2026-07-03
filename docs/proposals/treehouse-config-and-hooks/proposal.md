# Proposal: Treehouse-Inspired Sirius Worktree Config And Hooks

## Problem

`sirius worktree` may need explicit configuration and bootstrap rules so the
same packaged CLI can work against a shared worktree root when the derived
default is not enough. It also needs a safe way to adopt treehouse-like
lifecycle hooks without letting repo-local config smuggle in untrusted
destruction behavior.

## Goals

- Support an optional `sirius worktree` configuration surface only when the
  derived sibling `<repo>.worktrees` default is insufficient.
- Resolve the worktree pool root predictably from configuration or the safe
  default.
- Keep repo-level settings focused on safe behavior and ignore repo-level hooks.
- Allow user-level lifecycle hooks for create and destroy steps.
- Provide an `init` or config-inspection path only if the command needs a
  durable config file.
- Make the resolved worktree root discoverable in docs and command output.
- Run hooks sequentially through the OS shell and log failures without aborting
  the caller.

## Non-Goals

- A plugin runtime or hidden configuration loader.
- Hardcoding project-specific policy into the core CLI.
- Letting repo-local config override destructive hook behavior.
- Introducing `treehouse.toml` as a repo-owned source of truth unless the
  packaged `sirius` config model explicitly adopts it.

## Desired Outcome

Projects can adopt treehouse-like `sirius worktree` behavior with predictable
pool-root resolution and optional user-level hooks without losing portability.

## Success Criteria

- `sirius worktree` reports the resolved pool root clearly.
- Any repo and user config precedence matches documented behavior.
- The configured root resolves predictably and falls back to the derived
  sibling default.
- Hooks run sequentially and non-fatally at the configured lifecycle points.
- `sirius worktree` keeps the configured root clearly documented.

## Why This Is Still A Proposal

- Configuration and hooks define the project boundary around the CLI.
- This capability is separate from the pool lifecycle and reclamation rules.
