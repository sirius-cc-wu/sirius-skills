# Discover: Split Install Modes

## Parent Feature

- Feature: `installation-and-configuration`
- Subfeature ID: `split-install-modes`
- Subfeature Type: `superseding`

## Problem

`sirius-skills` currently treats managed packaged installation and normal local
agent usage as the same workflow. The result is unnecessary operational
complexity for contributors:

- local repo users do not need copied installed skill snapshots
- shared runtime files are copied into selected skill folders before install
- installed-vs-repo parity becomes part of ordinary maintenance behavior
- small repo-local fixes can remain hidden behind stale installed copies

This repo now has proof of that failure mode: the installed maintenance-skill
copies drifted behind the repo source and had to be reconciled manually even
though the local developer only needed the checked-in skills.

## Goals

- Add a source-linked local install path that exposes repo skills directly
  through `~/.agents/skills/` for clients that support native discovery.
- Keep the checked-in repo as the source of truth for local development.
- Preserve a packaged install path for agents or release flows that still need
  self-contained skill copies.
- Re-scope shared-runtime sync and installed parity checks to packaging and
  release boundaries instead of normal local usage.
- Document a migration path from the current `make install` behavior to the new
  split install model.

## Non-Goals

- Remove packaged standalone skill installs immediately.
- Rewrite the planning, execution, or workflow-state model.
- Introduce a general-purpose plugin loader beyond the current documented
  conventions.
- Require new `.skills/*.json` configuration files for local installation.

## Primary Actors

- Local contributor iterating on `sirius-skills` in a repo checkout.
- Maintainer packaging the managed skill set for broader agent compatibility.
- Reviewer diagnosing whether a problem belongs to local source behavior or a
  packaged export/install boundary.

## Constraints

- The repo must preserve backward-compatible behavior long enough for users to
  migrate from the current `make install` flow.
- Core skills must stay generic-first and avoid agent-specific runtime logic
  inside the skill bodies when a repo-level install helper is sufficient.
- Packaged maintenance skills may still need self-contained runtime folders when
  installed outside a repo checkout.
- Documentation and install commands must make the local-versus-packaged split
  obvious.

## Confirmed Signals in Repo

- `Makefile` currently installs all managed skills through `npx skills add`.
- `scripts/sync_shared_skill_runtime.py` exists to copy `lib/workflow_state/`
  into selected skill folders before packaged install.
- `workflow-state-consistency` planning explicitly introduced installed parity to
  guard that copied-runtime packaging model.
- `superpowers` demonstrates a simpler native-discovery pattern: one repo checkout plus
  symlinked discovery under `~/.agents/skills/`.

## Desired Outcomes

- Local developers can install the repo skill set without generating
  copied installed runtimes.
- Packaged install remains available, but becomes an explicit secondary mode.
- Normal local audit/report flows no longer need installed parity as a default
  safety net.
- The repo documentation explains when to use local symlink install versus
  packaged install.

## Candidate Capability Areas

- **Local source-linked install helpers**
  - create per-skill symlinks into `~/.agents/skills/`
  - remove those symlinks cleanly
  - support deterministic reruns for refresh behavior

- **Install-mode split**
  - separate local development install from packaged standalone install
  - rename or re-alias Make targets so the default path is explicit
  - keep the local target naming generic enough for multiple agent CLIs

- **Packaged-boundary hardening**
  - keep shared-runtime sync only for packaged/export flows
  - keep installed parity checks only where copied installs still exist

- **Migration guidance**
  - document the preferred local workflow
  - explain how existing packaged users transition safely

## Success Criteria

- A local developer can expose the repo skills directly through
  `~/.agents/skills/` without using `npx skills add`.
- The packaged install path remains available and clearly labeled as a distinct
  distribution mode.
- Shared-runtime sync and parity logic no longer drive ordinary local install
  behavior.
- The migration plan is explicit enough to stage the rollout without breaking
  current users.

## Risks and Open Questions

- Per-skill symlink install changes operator expectations for `make install`,
  so the repo needs a deliberate compatibility phase.
- Some maintained agents may still require packaged standalone skill folders,
  which means the packaged path cannot disappear immediately.
- The repo must decide when parity leaves default audit/report output and
  becomes an explicit packaged-release validation surface.
