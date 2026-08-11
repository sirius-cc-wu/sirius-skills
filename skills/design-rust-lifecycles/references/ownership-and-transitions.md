# Ownership and Transitions

## Resource Inventory

Record every value whose release, uniqueness, or transfer affects correctness.
Include ordinary memory only when allocation behavior is itself consequential.

| Resource or capability | Created by | Owner while prepared | Transfer | Owner while running | Explicit release | `Drop` fallback |
|---|---|---|---|---|---|---|
| [resource] | [operation] | [type] | [consuming operation] | [type] | [fallible operation] | [bounded behavior] |

Distinguish:

- an owned resource from a borrowed view;
- a configured address from an operating-system reservation;
- a task handle from the task it supervises;
- a path from the file, socket, or credential at that path; and
- permission to perform an action from the action's eventual result.

## Transition Selection

Prefer the smallest mechanism that makes invalid use acceptably difficult:

1. Use a consuming method when one aggregate changes phase and callers do not
   need to name the intermediate states.
2. Use a private enum when one public type must represent several runtime
   phases internally.
3. Use separate public state types when callers require different operations
   before and after a transition.
4. Use typestate or generic state markers only when compile-time enforcement
   prevents important misuse across a stable public API.

For each transition, record:

| From | Event | Consumes | Acquires or transfers | To | Failure result |
|---|---|---|---|---|---|
| [state] | [operation] | [`self` or handle] | [capabilities] | [state] | [error plus remaining ownership] |

An error must not make resource ownership ambiguous. If a consuming operation
can fail after partial transfer, return an error that owns the rollback report
or ensure rollback completes before the error returns.

## API Sketch Rules

- Use `&self` for observation and read-only views.
- Use `&mut self` for reversible exclusive mutation within one phase.
- Use `self` for irreversible phase changes and ownership transfer.
- Return iterators or borrowed slices when callers need views, not ownership.
- Keep invariant-bearing fields private.
- Use `Result<T, E>` for expected failure and preserve useful source context.
- Show whether handles are `Send`, `Sync`, task-local, thread-bound, or
  process-global when that affects composition.
