# Proposal: Batch Planning Orchestration

## Problem

`sirius-skills` has strong single-target skills for planning and delivery, but
natural maintainer prompts often refer to a collection:

- "apply discover to all of them"
- "apply plan skills to all of them"
- "apply autoplan to all"
- "approve all of them"
- "ship them all"

Today, those phrases require the coding agent to infer the target set, decide
which lifecycle phase is meant, and manually loop over individual features or
subfeatures. That works only when the agent keeps enough context and behaves
conservatively. It is too easy to skip targets, mix planning and execution
boundaries, or lose resumability during long-running batches.

The existing one-target contracts should remain intact. `discover`, `autoplan`,
and `ship` are safer because they resolve exactly one planning packet at a
time. The missing capability is a durable batch orchestrator that expands
"all" into an explicit target manifest and delegates each target to the
existing single-target skills sequentially.

## Proposed Capability

Add a first-class batch planning orchestration surface to `sirius-skills`.
The surface may be implemented as a new skill and CLI command, tentatively:

```text
sirius batch-planning inventory
sirius batch-planning discover --all
sirius batch-planning autoplan --all --execute-owner-chain
sirius batch-planning approve --all --approval-note "approved for execution"
sirius batch-planning ship --all
```

An equivalent naming scheme such as `plan-all` / `ship-all` is acceptable if it
keeps the same lifecycle semantics.

The orchestrator should not author discovery, design, breakdown, execution, or
closure artifacts itself. It should resolve target sets, record progress, call
the existing owner skills or CLI helpers for one target at a time, and stop at
explicit human or repository safety boundaries.

## Desired Workflow

### Phase 1: Discover All

When a maintainer says:

```text
Apply discover to all features and subfeatures under docs/features.
Stop when discovery is ready for my review.
```

The orchestrator should:

1. Inventory all canonical feature and subfeature planning targets.
2. Select targets whose discovery is missing, still draft, still pending, or a
   known bootstrap stub.
3. Invoke the `discover` skill for each selected target.
4. For canonical features, advance metadata to `discovery_ready` through the
   normal planning status tooling.
5. For subfeatures, preserve subfeature lifecycle ownership in
   `.subfeature-meta.json` and leave downstream routing to `design`.
6. Stop after discovery artifacts are ready for human review.

### Phase 2: Human Discovery Review

The maintainer reviews all generated `discover.md` and `user-stories.md` files,
then discusses corrections with the coding agent as needed.

The batch orchestrator should not automatically continue from discovery into
design unless the maintainer explicitly asks.

### Phase 3: Autoplan All

When a maintainer says:

```text
Apply autoplan to all discovery-ready targets.
Stop at approval gates. Do not start execution.
```

The orchestrator should:

1. Select all targets ready for planning beyond discovery.
2. Run the existing one-target `autoplan` flow with owner-chain execution where
   appropriate.
3. Delegate artifact authoring to `design`, `breakdown`, and
   `review-planning` as directed by the single-target autoplan handoff.
4. Continue each target until a real stop boundary is reached:
   `planning_reviewed`, `approval_required`, `commit_checkpoint`,
   `owner_stop`, validation failure, or unresolved ambiguity.
5. Stop before execution slices are created.

### Phase 4: Human Planning Review

The maintainer reviews all generated planning artifacts, including
`system-design.md`, `slice-planning.md`, and `slice-traceability.md`.

The batch orchestrator should preserve an explicit approval gate. It should not
infer approval from the existence of reviewed planning files.

### Phase 5: Approve All

When a maintainer says:

```text
Approve all reviewed planning targets.
```

The orchestrator should:

1. Select only targets already at the reviewed planning boundary.
2. Refuse approval for blocked, stale, invalid, or dirty targets.
3. Record durable approval per target using the existing approval surfaces.
4. Hand approved-but-uncommitted planning to the existing commit checkpoint
   rather than silently proceeding into execution.

### Phase 6: Ship All

When a maintainer says:

```text
Ship them all, one target and one slice at a time.
```

The orchestrator should:

1. Select approved and committed targets with remaining planned slices.
2. Call the existing one-target `ship` flow sequentially.
3. Preserve current execution guardrails: one active target, one active slice,
   one commit per completed slice, and explicit stops at review or repository
   safety boundaries.
4. Stop and report when a target needs human review, a commit checkpoint, a
   failed validation fix, or a missing decision.

## Batch Manifest

Add a durable runtime manifest for resumability, for example:

```text
.skills/runtime/batches/<batch-id>.json
```

The manifest should include:

```json
{
  "batch_id": "batch-planning-2026-07-12T10-00-00",
  "phase": "autoplan",
  "target_selector": "all",
  "current_index": 0,
  "targets": [
    {
      "path": "docs/features/cli-launch",
      "kind": "feature",
      "status_before": "discovery_ready",
      "status_after": "planning_reviewed",
      "result": "approval_required",
      "stop_reason": "approval_required"
    }
  ]
}
```

The manifest should be derived from repository artifacts and runtime events. It
should not become a second source of truth for target lifecycle state.

## Target Resolution

The batch surface should reuse existing planning registry behavior:

- Canonical feature targets come from `docs/features/registry.json` and
  `.planning-meta.json`.
- Subfeature targets come from feature-local `subfeatures/registry.json` and
  `.subfeature-meta.json`.
- Nested planning scopes must be explicit when ambiguous.
- Implemented or archived parent features should not be reopened for new delta
  work; follow-on work should still route through subfeatures.

## Skill Trigger Text

The new skill should explicitly claim these maintainer prompts:

- "apply discover to all features"
- "apply discover to all of them"
- "apply plan skills to all of them"
- "apply autoplan to all"
- "approve all planning packets"
- "approve all of them"
- "ship them all"
- "ship all slices"

The skill should translate those phrases into the corresponding batch phase and
should ask for clarification only when the phase or scope is genuinely
ambiguous.

## Guardrails

- Do not modify `references/`.
- Do not collapse all work into one large execution run.
- Do not make `autoplan` or `ship` inherently multi-target; keep them safe
  single-target primitives.
- Do not start execution during discovery or autoplan phases.
- Do not approve planning without an explicit maintainer approval request.
- Do not continue past dirty worktree, validation, review, or commit
  checkpoints.
- Do not treat the runtime manifest as lifecycle truth; use planning and
  execution artifacts as the source of truth.

## Acceptance Criteria

- A maintainer can ask to apply discovery across all planning targets and get a
  complete, resumable per-target result.
- A maintainer can review discovery, then ask to apply autoplan across all
  discovery-ready targets.
- The autoplan batch stops at approval gates and does not create execution
  slices.
- A maintainer can approve all reviewed targets with one explicit approval
  request, while invalid or stale targets are skipped with reasons.
- A maintainer can ship all approved targets, with delivery still proceeding
  sequentially through the existing one-target `ship` and `ship-slice`
  contracts.
- Interrupted batches can resume without relying on private chat context.

## Why This Is Still A Proposal

The exact command and skill names should be accepted before implementation.
The capability crosses planning, approval, and execution orchestration, so it
should be promoted into canonical planning only after the team agrees on the
batch lifecycle boundaries and safety model.
