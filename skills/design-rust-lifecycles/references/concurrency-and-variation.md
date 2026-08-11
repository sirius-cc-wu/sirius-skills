# Concurrency and Variation

## Concurrency Ownership

Give every spawned task, thread, and child process an owner and a shutdown
path. Record:

| Participant | Spawned by | Supervising owner | Shared state | Readiness | Cancellation | Join or reap |
|---|---|---|---|---|---|---|
| [participant] | [operation] | [type/task] | [none/channel/lock] | [proof] | [signal] | [operation] |

Prefer structured lifetimes in which child work cannot silently outlive its
owner. Use channels and owned messages before shared mutation. Introduce
`Arc`, locks, atomics, and `Send + Sync` only where a real cross-task or
cross-thread boundary requires them. State ordering, backpressure, and failure
propagation for channels.

Readiness must prove that the participant being started owns or produced the
ready condition. File or socket-path existence alone is insufficient when the
path may be stale or shared.

## Variation Mechanism

Choose the smallest mechanism supported by current evidence:

| Variation shape | Prefer |
|---|---|
| One stable implementation | Concrete type or function |
| Closed alternatives controlled by the crate | `enum` plus exhaustive match |
| Compile-time algorithm or adapter choice | Generic bound |
| One locally varying operation | Closure or `Fn*` bound |
| Runtime-selected heterogeneous implementations | Trait object |
| Unstable external API with trivial translation | Wrapper or conversion function |
| Coherent module-level responsibility | Private module API |

For every trait or abstraction, record:

- the demonstrated source of variation;
- whether selection is compile-time or runtime;
- ownership and thread-safety requirements;
- which consumer owns the contract; and
- the event that would justify extraction if it is deferred.

Do not introduce an allocator, coordinator, provider, service, or manager type
solely to preserve symmetry with a language-neutral design diagram.
