# Failure, Cancellation, and Cleanup

## Preparation and Commit Boundary

Identify the last point before externally visible work begins. Validate and
acquire everything that can be checked safely before that point. Keep endpoint,
lock, lease, and name reservations alive until the consumer takes ownership;
do not probe, release, and later reacquire.

Use this matrix:

| Failure or cancellation point | Resources already acquired or started | Required compensation | Primary result | Cleanup evidence |
|---|---|---|---|---|
| [point] | [owned items] | [ordered actions] | [preserved error/outcome] | [report or observation] |

## Rollback

- Record a started handle immediately after each successful start.
- Roll back in reverse acquisition order unless a protocol requires another
  order.
- Attempt independent cleanup actions even after one fails.
- Preserve the original startup, validation, completion, or abort reason.
- Report cleanup failures separately and redact secrets at the reporting
  boundary.
- Prefer a guard that owns partial state when cancellation between acquisition
  and registration would otherwise leak it.

## Async Cancellation

For every relevant `.await`, answer:

1. What owned values are dropped if the future is cancelled here?
2. Does `Drop` release them completely, only initiate release, or do nothing?
3. Can a child task, process, lease, lock, or remote operation outlive its
   intended owner?
4. Must cleanup be cancellation-resistant, delegated to a supervisor, or
   resumed by another owner?
5. How is cancellation distinguished from an ordinary failure in reports?

Avoid claiming that `kill_on_drop`, task abortion, or file deletion also waits
for termination, reaps a process, drains work, flushes data, or reports errors
unless the API actually guarantees it.

## RAII and Explicit Termination

Use RAII for bounded, synchronous, infallible release. Add an explicit
`close`, `shutdown`, `finish`, `complete`, or `abort` operation when:

- cleanup can fail;
- ordering matters;
- asynchronous work must finish;
- a process or task must be joined or reaped;
- data must be flushed or committed; or
- callers need a cleanup report.

Keep `Drop` as a safe, non-blocking emergency fallback. Document what it can
and cannot guarantee. Never block an async runtime or hide an unbounded wait in
`Drop`.
