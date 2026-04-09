# Behavioral Systems Guidance

Read this reference when the feature includes any of the following:

- shared mutable state
- connection or session reuse
- caches keyed by request or route metadata
- retry or reconnection behavior
- routing or dispatch across multiple backends
- protocol translation or error mapping
- concurrency control or lock layering

## What to document explicitly

When these patterns exist, `system-design.md` should capture:

1. Ownership scope
   - who owns the shared manager, cache, registry, or connection pool
   - whether ownership is process-global, server-scoped, request-scoped, or client-scoped

2. Concurrency model
   - which synchronization primitives exist
   - what each lock or gate protects
   - what work is intentionally serialized versus parallel-safe

3. Invariants
   - uniqueness rules
   - lifecycle guarantees
   - ordering constraints
   - invalidation or cleanup guarantees

4. Effective lifecycle model
   - explicit states when the code models them directly
   - effective states when the runtime behavior is implicit in entry presence, cached values, or ownership

5. Success path
   - the normal request or event flow from entry to completion

6. Failure and recovery semantics
   - what fails fast
   - what is retried immediately
   - what is invalidated and retried only by a later request
   - what cleanup or invalidation happens after failure

7. Error mapping across boundaries
   - how lower-layer or dependency errors map to higher-layer responses, statuses, or NACKs

## Useful section names

Use section names like these when they fit:

- `Locking and concurrency model`
- `Lifecycle model`
- `Failure and reconnect behavior`
- `Error handling policy`
- `Request flow`

## Common failure in weak designs

Do not leave these implied:

- whether one request is retried or only a later request reconnects
- whether a cached entry is removed, reset, or kept after failure
- whether one shared client can process requests concurrently
- whether ownership is server-scoped or global
- how transport or dependency errors surface to callers

These details often determine correctness, operability, and later slice boundaries.
