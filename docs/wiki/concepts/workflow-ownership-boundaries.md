# Workflow Ownership Boundaries

## Why This Matters

Across feature packets, the strongest recurring architectural rule is explicit
ownership by workflow layer. Most capabilities are additive orchestration around
existing owners, not replacements.

## Stable Ownership Model

- Planning ownership:
  - `guide-planning` owns planning readiness and planning registry state.
  - Planning authoring skills own planning artifacts.
- Execution ownership:
  - `guide-execution` owns slice readiness and execution registry state.
  - new subfeature execution slices live under the owning subfeature's local
    `slices/` root.
  - `blueprint` owns the new-slice contract, implementation plan, validation
    mapping, and detailed design.
  - `brief` and `brief_ready` are legacy or explicit-clarification surfaces, not
    mandatory new-slice owners.
  - `review-execution` and `close-slice` own closure quality and closure writes.
- Maintenance ownership:
  - cross-artifact skills inspect, report, and repair derived drift, but avoid
    replacing planning/execution lifecycle owners.

## State Model Conclusion

- Durable source of truth remains repository artifacts (`docs/features/`,
  `docs/proposals/`, `slices/`, and metadata files).
- Supplemental runtime state (checkpoint logs, event logs, learnings) can guide
  execution flow but must reconcile back to durable repo truth.
- Non-destructive history is preferred; archival and cleanup are explicit,
  reviewable operations.

## Practical Implication For New Work

When adding capabilities, prefer:

1. additive orchestration
2. shared parsing/reconciliation helpers
3. explicit boundaries between lifecycle writes and reporting/repair logic

Avoid monolithic skills that hide or rewrite owner responsibilities.

## Main Sources

- `docs/features/planning-workflow/system-design.md`
- `docs/features/execution-workflow/system-design.md`
- `docs/features/workflow-state-consistency/system-design.md`
- `docs/features/throughput-acceleration-workflow/system-design.md`
- `docs/features/cross-artifact-management/discover.md`
