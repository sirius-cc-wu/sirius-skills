# Proposal: Treehouse Config And Hooks

## Problem

Treehouse needs explicit configuration and bootstrap rules so the same CLI can
work against a shared treehouse root. It also needs a safe way to run lifecycle
hooks without letting repo-local config smuggle in untrusted destruction
behavior.

## Goals

- Support a repo-level `treehouse.toml` and a user-level config file.
- Resolve the treehouse root from configuration, with a safe default when none
  is set.
- Keep repo-level settings focused on safe behavior and ignore repo-level hooks.
- Allow user-level lifecycle hooks for create and destroy steps.
- Provide an `init` command that writes a default repo config.
- Make the treehouse root discoverable in docs and config output.
- Run hooks sequentially through the OS shell and log failures without aborting
  the caller.

## Non-Goals

- A plugin runtime or hidden configuration loader.
- Hardcoding project-specific policy into the core CLI.
- Letting repo-local config override destructive hook behavior.

## Desired Outcome

Projects can adopt treehouse with a small local config file, user-level hooks,
and predictable treehouse-root resolution without losing portability.

## Success Criteria

- `treehouse init` writes a repo config with safe defaults.
- Repo and user config precedence matches the documented behavior.
- The configured root resolves predictably and falls back to the shared default.
- Hooks run sequentially and non-fatally at the configured lifecycle points.
- Treehouse keeps the configured root clearly documented.

## Why This Is Still A Proposal

- Configuration and hooks define the project boundary around the CLI.
- This capability is separate from the pool lifecycle and reclamation rules.
