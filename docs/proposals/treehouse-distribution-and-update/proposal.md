# Proposal: Treehouse Distribution And Update

## Problem

Treehouse is distributed as a cross-platform CLI, so it needs a clear story for
installation, release discovery, and updating the running binary. That story
must be safe enough to verify downloaded assets and simple enough to work from
the command line without a separate package manager integration.

## Goals

- Provide installation paths for source, Go, Nix, and shell bootstrap scripts.
- Detect the currently running version and show update notices when a newer
  release exists.
- Cache update checks so the CLI does not hit the network on every run.
- Offer an explicit `treehouse update` command for applying a release.
- Download platform-specific release archives and verify checksums before
  replacement.
- Keep the update flow cross-platform, including archive formats and executable
  replacement behavior.

## Non-Goals

- Background auto-update without user action.
- A package-manager-specific distribution lock-in.
- Skipping HTTPS or checksum validation for convenience.

## Desired Outcome

Users can install treehouse through the supported channels, get a safe notice
when a newer release exists, and update the binary in place when they choose.

## Success Criteria

- `treehouse update` reports the current state and only applies a newer release.
- Downloaded binaries are verified before replacement.
- The update flow works on Linux, macOS, and Windows.
- Update checks are cached and do not spam the release endpoint.

## Why This Is Still A Proposal

- Distribution and updating are a separate capability from worktree management.
- The release/update path needs to stay explicit and opt-in.
