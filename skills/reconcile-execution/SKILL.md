---
name: reconcile-execution
description: Reviews one completed feature or subfeature against final implementation and slice artifacts, then records a durable reconciliation block before archive.
---

# Reconcile Execution

Use this skill after all planned slices for one feature or subfeature are
closed, and before archival.

## Responsibilities

1. Review the completed implementation against the canonical `system-design.md`.
2. Compare scope-level design claims with the completed slice blueprints,
   validation evidence, and caller-visible behavior.
3. Update `system-design.md` so intentional execution drift is either removed or
   documented explicitly.
4. Record a durable reconciliation block in `system-design.md` that declares the
   scope aligned and names the planned slice IDs reviewed.

## Preferred Input

- one feature slug, subfeature slug, or planning packet path
- the target `system-design.md`
- the target `slice-planning.md`
- the target `slice-traceability.md`
- completed execution slice blueprints and closure evidence

## Required Durable Output

Write one reconciliation block in the target `system-design.md`:

```md
<!-- execution-reconciliation:start -->
Status: aligned
Reviewed Planned Slice IDs: slice-a, slice-b
Summary:
- scope-level design and completed slice execution have been reconciled
<!-- execution-reconciliation:end -->
```

Rules:

- `Status` must be `aligned`
- `Reviewed Planned Slice IDs` must name every completed planned slice that the
  archive step will summarize
- keep the summary concise and behavioral rather than process-heavy

## Workflow

1. Resolve the feature or subfeature scope.
2. Read `system-design.md`, `slice-planning.md`, `slice-traceability.md`, and
   the completed slice blueprints.
3. Check for drift in API contracts, UML, lifecycle behavior, and
   operator-visible outcomes.
4. Update `system-design.md` until it matches the final behavior or explicitly
   explains any intentional deviation.
   - When the final design relies on sequence-heavy execution behavior, keep at
     least one structural class/component-style diagram in the canonical
     `system-design.md` so later archive summaries do not have to invent that
     context.
5. Add or refresh the reconciliation block with `Status: aligned` and the full
   set of reviewed planned slice IDs.

## Guardrails

- Do not archive slices from this skill.
- Do not treat archived summaries as a substitute for reconciling the canonical
  `system-design.md`.
- Do not mark the reconciliation block `aligned` while known behavior drift is
  still unresolved.
- Do not defer missing structural context to `archive-artifacts`; preserve or
  add the canonical class/component-style diagram here when execution depends on
  it.
- Keep the reconciliation record generic and durable; avoid project-local review
  ceremony or tracker-specific fields.
